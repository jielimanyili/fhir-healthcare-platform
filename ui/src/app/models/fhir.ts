export interface Coding {
  system?: string;
  code?: string;
  display?: string;
}

export interface HumanName {
  use?: string;
  family?: string;
  given?: string[];
}

export interface Patient {
  resourceType: 'Patient';
  id?: string;
  name?: HumanName[];
  gender?: string;
  birthDate?: string;
}

export interface Reference {
  reference?: string;
  display?: string;
}

export interface Quantity {
  value?: number;
  unit?: string;
}

export interface Observation {
  resourceType: 'Observation';
  id?: string;
  status: string;
  code?: { coding?: Coding[]; text?: string };
  subject?: Reference;
  valueQuantity?: Quantity;
}

export interface Claim {
  resourceType: 'Claim';
  id?: string;
  status: string;
  patient?: Reference;
  total?: { value?: number; currency?: string };
}

export interface Bundle<T> {
  resourceType: 'Bundle';
  type: 'searchset';
  total: number;
  entry?: { resource: T }[];
}
