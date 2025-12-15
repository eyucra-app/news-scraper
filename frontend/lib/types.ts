// Tipos para las entidades del sistema
export interface NewsSource {
    id: number;
    name: string;
    url: string;
    container: string;
    holder: string;
    data_field?: string | null;
    category: string;
    is_active: boolean;
    requires_js?: boolean;
    scrape_count: number;
    error_count: number;
    last_scraped_at?: string | null;
    created_at: string;
    updated_at: string;
}

export interface Headline {
    id: number;
    title: string;
    source_id: number;
    source_name?: string;
    category: string;
    content_hash: string;
    sent_to_singular: boolean;
    sent_at?: string | null;
    created_at: string;
}

export interface ScrapeStats {
    total: number;
    sent: number;
    unsent: number;
    by_category: Record<string, number>;
}

export interface ScrapingResult {
    status: string;
    stats: {
        sources_scraped: number;
        headlines_found: number;
        headlines_new: number;
        errors: number;
    };
}

export interface SchedulerStatus {
    running: boolean;
    paused: boolean;
    next_run?: string | null;
    interval_minutes?: number | null;
}

export interface HealthStatus {
    status: string;
    redis: string;
    environment: string;
}

export interface AppConfig {
    singular: {
        control_app_id: string;
        output_url: string;
        has_config: boolean;
    };
    scraping_interval: number;
    environment: string;
    debug: boolean;
}

export type Category = 'local' | 'nacional' | 'mundo' | 'deportes' | 'tecnologia' | 'economia' | 'entretenimiento' | 'otro';
