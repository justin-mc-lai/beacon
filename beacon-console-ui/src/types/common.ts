export interface ApiResponse<T> {
  success: boolean;
  data?: T;
  error?: string;
  message?: string;
}

export interface PaginationParams {
  page: number;
  pageSize: number;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  pageSize: number;
}

export interface TraceLink {
  label: string;
  path: string;
  note: string;
}

export interface PageTrace {
  pageId: string;
  pageName: string;
  freezeLinks: TraceLink[];
  currentSpecLinks: TraceLink[];
  acceptanceCriteria: string[];
}
