export type LinkItem = {
  code: string;
  original_url: string;
  short_url: string;
  short_domain?: string | null;
  redirect_type: string;
  description?: string | null;
  channel?: string | null;
  has_password: boolean;
  meta_title?: string | null;
  meta_description?: string | null;
  meta_image_url?: string | null;
  click_count: number;
  created_at: string;
};

export type LinkListResponse = {
  items: LinkItem[];
  total: number;
};

export type CreateLinkPayload = {
  url: string;
  custom_code?: string;
  domain?: string;
  redirect_type?: "direct";
  description?: string;
  channel?: string;
  password?: string;
  meta_title?: string;
  meta_description?: string;
  meta_image_url?: string;
};

export type BulkCreatePayload = {
  urls: string[];
  domain?: string;
  redirect_type?: "direct";
  description?: string;
  channel?: string;
};
