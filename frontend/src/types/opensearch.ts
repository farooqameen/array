export interface Source {
  chunk_id: string;
  text: string;
  title: string | null;
  chapter: string | null;
  section: string | null;
  header: string | null;
  page_number: number;
  batch_number: number;
  original_pdf_filename: string;
  word_count: number;
  timestamp: string;
  s3_link: string;
}

export interface Hit {
  _index: string;
  _id: string;
  _score: number;
  _source: Source;
  highlight?: {
    text: string[];
  };
}

export interface Total {
  value: number;
  relation: string;
}

export interface Hits {
  total: Total;
  max_score: number;
  hits: Hit[];
}

export interface OpenSearchResult {
  took: number;
  timed_out: boolean;
  _shards: {
    total: number;
    successful: number;
    skipped: number;
    failed: number;
  };
  hits: Hits;
}
