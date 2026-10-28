package com.fhir.pipeline;

import com.fasterxml.jackson.databind.JsonNode;
import com.fasterxml.jackson.databind.ObjectMapper;
import com.google.cloud.bigquery.BigQuery;
import com.google.cloud.bigquery.BigQueryOptions;
import com.google.cloud.bigquery.InsertAllRequest;
import com.google.cloud.bigquery.TableId;
import com.google.cloud.pubsub.v1.AckReplyConsumer;
import com.google.cloud.pubsub.v1.MessageReceiver;
import com.google.cloud.pubsub.v1.Subscriber;
import com.google.pubsub.v1.ProjectSubscriptionName;
import com.google.pubsub.v1.PubsubMessage;
import jakarta.annotation.PreDestroy;
import java.util.HashMap;
import java.util.Map;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.CommandLineRunner;
import org.springframework.stereotype.Component;

/**
 * Consumes FHIR resource events from Pub/Sub and writes denormalized rows to
 * BigQuery. This is the Java (Spring Boot) component from ADR-0004 — the GCP
 * analog of the COP Data Platform (Kafka Streams).
 */
@Component
public class FhirEventPipeline implements CommandLineRunner {

    private static final Logger log = LoggerFactory.getLogger(FhirEventPipeline.class);

    private final ObjectMapper mapper = new ObjectMapper();
    private final BigQuery bigQuery = BigQueryOptions.getDefaultInstance().getService();
    private Subscriber subscriber;

    @Value("${gcp.project-id}")
    private String projectId;

    @Value("${gcp.subscription}")
    private String subscriptionId;

    @Value("${gcp.bigquery.dataset}")
    private String dataset;

    @Override
    public void run(String... args) {
        ProjectSubscriptionName subscription = ProjectSubscriptionName.of(projectId, subscriptionId);
        MessageReceiver receiver = this::handle;
        subscriber = Subscriber.newBuilder(subscription, receiver).build();
        subscriber.startAsync().awaitRunning();
        log.info("Listening on subscription {}", subscription);
        subscriber.awaitTerminated();
    }

    private void handle(PubsubMessage message, AckReplyConsumer consumer) {
        try {
            JsonNode resource = mapper.readTree(message.getData().toStringUtf8());
            String resourceType = resource.path("resourceType").asText();
            if ("Claim".equals(resourceType)) {
                insert(dataset, "claims", claimRow(resource));
            } else if ("Observation".equals(resourceType)) {
                insert(dataset, "observations", observationRow(resource));
            } else {
                log.info("Skipping resource type {}", resourceType);
            }
            consumer.ack();
        } catch (Exception e) {
            log.error("Failed to process message", e);
            consumer.nack();
        }
    }

    private Map<String, Object> claimRow(JsonNode claim) {
        Map<String, Object> row = new HashMap<>();
        row.put("id", claim.path("id").asText());
        row.put("status", claim.path("status").asText());
        row.put("patient", claim.path("patient").path("reference").asText());
        row.put("total", claim.path("total").path("value").asDouble());
        return row;
    }

    private Map<String, Object> observationRow(JsonNode obs) {
        Map<String, Object> row = new HashMap<>();
        row.put("id", obs.path("id").asText());
        row.put("status", obs.path("status").asText());
        row.put("subject", obs.path("subject").path("reference").asText());
        row.put("code", obs.path("code").path("coding").get(0).path("code").asText());
        row.put("value", obs.path("valueQuantity").path("value").asDouble());
        return row;
    }

    private void insert(String datasetName, String table, Map<String, Object> row) {
        TableId tableId = TableId.of(projectId, datasetName, table);
        InsertAllRequest request = InsertAllRequest.newBuilder(tableId).addRow(row).build();
        bigQuery.insertAll(request);
        log.info("Inserted row into {}.{}", datasetName, table);
    }

    @PreDestroy
    public void shutdown() {
        if (subscriber != null) {
            subscriber.stopAsync();
        }
    }
}
