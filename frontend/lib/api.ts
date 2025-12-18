import {
    NewsSource,
    Headline,
    ScrapeStats,
    ScrapingResult,
    SchedulerStatus,
    HealthStatus,
    AppConfig,
} from './types';

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000/api';
const BACKEND_BASE_URL = process.env.NEXT_PUBLIC_API_URL?.replace('/api', '') || 'http://localhost:8000';
const REQUEST_TIMEOUT = 10000; // 10 segundos

// Estado del backend
let backendAvailable: boolean | null = null;

// Helper para detectar disponibilidad del backend
export async function checkBackendAvailability(): Promise<boolean> {
    try {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), 3000); // 3 segundos para health check

        const response = await fetch(`${BACKEND_BASE_URL}/health`, {
            signal: controller.signal,
        });

        clearTimeout(timeoutId);
        backendAvailable = response.ok;
        return response.ok;
    } catch (error) {
        backendAvailable = false;
        return false;
    }
}

// Obtener estado actual del backend (sin hacer request)
export function isBackendAvailable(): boolean | null {
    return backendAvailable;
}

// Helper para manejar errores con timeout
async function handleResponse<T>(response: Response): Promise<T> {
    if (!response.ok) {
        const error = await response.text();
        throw new Error(`API Error: ${response.status} - ${error}`);
    }
    return response.json();
}

// Helper para fetch con timeout
async function fetchWithTimeout(url: string, options: RequestInit = {}): Promise<Response> {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), REQUEST_TIMEOUT);

    try {
        const response = await fetch(url, {
            ...options,
            signal: controller.signal,
        });
        clearTimeout(timeoutId);
        return response;
    } catch (error) {
        clearTimeout(timeoutId);
        if (error instanceof Error && error.name === 'AbortError') {
            throw new Error('Backend no disponible: tiempo de espera agotado');
        }
        throw new Error('Backend no disponible: verifica que el backend esté ejecutándose localmente');
    }
}

// ==================== SOURCES ====================

export async function getSources(activeOnly = false): Promise<NewsSource[]> {
    const url = activeOnly ? `${API_BASE_URL}/sources/?active_only=true` : `${API_BASE_URL}/sources/`;
    const response = await fetchWithTimeout(url);
    return handleResponse<NewsSource[]>(response);
}

export async function getSource(id: number): Promise<NewsSource> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}`);
    return handleResponse<NewsSource>(response);
}

export async function createSource(data: Partial<NewsSource>): Promise<NewsSource> {
    const response = await fetch(`${API_BASE_URL}/sources/`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    return handleResponse<NewsSource>(response);
}

export async function updateSource(id: number, data: Partial<NewsSource>): Promise<NewsSource> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data),
    });
    return handleResponse<NewsSource>(response);
}

export async function deleteSource(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}`, {
        method: 'DELETE',
    });
    // 204 No Content es exitoso pero no tiene body
    if (!response.ok && response.status !== 204) {
        const error = await response.text();
        throw new Error(`Failed to delete source: ${response.status} - ${error}`);
    }
}

export async function testSource(id: number): Promise<ScrapingResult> {
    const response = await fetch(`${API_BASE_URL}/sources/${id}/test`, {
        method: 'POST',
    });
    return handleResponse<ScrapingResult>(response);
}

// ==================== SCRAPING ====================

export async function startScraping(): Promise<ScrapingResult> {
    const response = await fetch(`${API_BASE_URL}/scraping/start`, {
        method: 'POST',
    });
    return handleResponse<ScrapingResult>(response);
}

export async function getScrapingStatus(): Promise<SchedulerStatus> {
    const response = await fetch(`${API_BASE_URL}/scraping/status`);
    return handleResponse<SchedulerStatus>(response);
}

export async function startScheduler(intervalMinutes = 5): Promise<{ message: string }> {
    const response = await fetch(
        `${API_BASE_URL}/scraping/scheduler/start?interval_minutes=${intervalMinutes}`,
        { method: 'POST' }
    );
    return handleResponse<{ message: string }>(response);
}

export async function stopScheduler(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/scraping/scheduler/stop`, {
        method: 'POST',
    });
    return handleResponse<{ message: string }>(response);
}

export async function pauseScheduler(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/scraping/scheduler/pause`, {
        method: 'POST',
    });
    return handleResponse<{ message: string }>(response);
}

export async function resumeScheduler(): Promise<{ message: string }> {
    const response = await fetch(`${API_BASE_URL}/scraping/scheduler/resume`, {
        method: 'POST',
    });
    return handleResponse<{ message: string }>(response);
}

// ==================== HEADLINES ====================

export async function getHeadlines(params?: {
    limit?: number;
    offset?: number;
    category?: string;
    sourceId?: number;
    unsentOnly?: boolean;
}): Promise<Headline[]> {
    const searchParams = new URLSearchParams();
    if (params?.limit) searchParams.append('limit', params.limit.toString());
    if (params?.offset) searchParams.append('offset', params.offset.toString());
    if (params?.category) searchParams.append('category', params.category);
    if (params?.sourceId) searchParams.append('source_id', params.sourceId.toString());
    if (params?.unsentOnly) searchParams.append('unsent_only', 'true');

    const url = `${API_BASE_URL}/headlines/?${searchParams.toString()}`;
    const response = await fetch(url);
    return handleResponse<Headline[]>(response);
}

export async function getHeadlineStats(): Promise<ScrapeStats> {
    const response = await fetch(`${API_BASE_URL}/headlines/stats`);
    return handleResponse<ScrapeStats>(response);
}

export async function sendHeadlinesToSingular(headlineIds: number[]): Promise<{ status: string; sent: number }> {
    const response = await fetch(`${API_BASE_URL}/headlines/send`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ headline_ids: headlineIds }),
    });
    return handleResponse<{ status: string; sent: number }>(response);
}

export async function deleteHeadline(id: number): Promise<void> {
    const response = await fetch(`${API_BASE_URL}/headlines/${id}`, {
        method: 'DELETE',
    });
    if (!response.ok) {
        throw new Error(`Failed to delete headline: ${response.status}`);
    }
}

// ==================== CONFIG ====================

export async function getConfig(): Promise<AppConfig> {
    const response = await fetch(`${API_BASE_URL}/config/`);
    return handleResponse<AppConfig>(response);
}

export async function updateSingularConfig(controlAppId: string): Promise<{ status: string; message: string; connection_test?: string }> {
    const response = await fetch(`${API_BASE_URL}/config/singular`, {
        method: 'PUT',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            control_app_id: controlAppId
        }),
    });
    return handleResponse<{ status: string; message: string; connection_test?: string }>(response);
}

export async function testSingularConnection(): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/config/test-singular`, {
        method: 'POST',
    });
    return handleResponse<{ status: string; message: string }>(response);
}

// ==================== TICKER CONTROL ====================

export async function controlTicker(
    state: 'In' | 'Out',
    category: string = 'mundo',
    maxHeadlines: number = 10,
    separatorUrl: string = 'https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg',
    showSourceName: boolean = true,
    autoScrape: boolean = false,
    scrapingInterval: number = 10  // NUEVO - intervalo de scraping para modo manual
): Promise<{ status: string; message: string; ticker_state?: string; headlines_count?: number }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/control`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            state,
            category,
            max_headlines: maxHeadlines,
            separator_url: separatorUrl,
            show_source_name: showSourceName,
            auto_scrape: autoScrape,
            scraping_interval: scrapingInterval  // NUEVO
        }),
    });
    return handleResponse<{ status: string; message: string; ticker_state?: string; headlines_count?: number }>(response);
}

// ==================== ROTACIÓN AUTOMÁTICA ====================

export async function startTickerRotation(
    intervalSeconds: number = 60,
    separatorUrl: string = 'https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg',
    showSourceName: boolean = true
): Promise<{ status: string; message: string; rotation_status: any }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/rotation/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            interval_seconds: intervalSeconds,
            separator_url: separatorUrl,
            show_source_name: showSourceName
        }),
    });
    return handleResponse<{ status: string; message: string; rotation_status: any }>(response);
}

export async function stopTickerRotation(): Promise<{ status: string; message: string; rotation_status: any }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/rotation/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
    });
    return handleResponse<{ status: string; message: string; rotation_status: any }>(response);
}

export async function getTickerRotationStatus(): Promise<{ status: string; rotation_status: any }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/rotation/status`);
    return handleResponse<{ status: string; rotation_status: any }>(response);
}

export async function updateSchedulerInterval(intervalMinutes: number): Promise<{ status: string; message: string; interval_minutes?: number }> {
    const response = await fetch(`${API_BASE_URL}/scraping/scheduler/interval?interval_minutes=${intervalMinutes}`, {
        method: 'PUT'
    });
    return handleResponse<{ status: string; message: string; interval_minutes?: number }>(response);
}

export async function updateTickerSeparator(separatorUrl: string): Promise<{ status: string; message: string }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/separator`, {
        method: 'PATCH',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ separator_url: separatorUrl }),
    });
    return handleResponse<{ status: string; message: string }>(response);
}

// ==========================================
// API: Modo Automático
// ==========================================

export interface AutoModeStatus {
    auto_mode_active: boolean;
    scheduler_running: boolean;
    rotation_running: boolean;
    current_category: string | null;
    next_rotation_in: number | null;
    next_scraping_in: number | null;
    started_at: string | null;
    scraping_interval_minutes: number;
    rotation_interval_seconds: number;
}

export async function startAutoMode(
    rotationInterval: number,
    scrapingInterval: number,
    showSourceName: boolean
): Promise<{ status: string; message: string; auto_mode_active: boolean }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/auto/start`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            rotation_interval: rotationInterval,
            scraping_interval: scrapingInterval,
            show_source_name: showSourceName
            // separator_url eliminado - se usa el configurado globalmente
        })
    });
    return handleResponse<{ status: string; message: string; auto_mode_active: boolean }>(response);
}

export async function stopAutoMode(): Promise<{ status: string; message: string; auto_mode_active: boolean }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/auto/stop`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
    });
    return handleResponse<{ status: string; message: string; auto_mode_active: boolean }>(response);
}

export async function getAutoModeStatus(): Promise<{ status: string } & AutoModeStatus> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/auto/status`);
    return handleResponse<{ status: string } & AutoModeStatus>(response);
}

export async function getTickerState(): Promise<{ status: string; state: 'In' | 'Out' | null; message: string }> {
    const response = await fetch(`${API_BASE_URL}/scraping/ticker/state`);
    return handleResponse<{ status: string; state: 'In' | 'Out' | null; message: string }>(response);
}


// ==================== HEALTH ====================

export async function getHealth(): Promise<HealthStatus> {
    const response = await fetchWithTimeout(`${BACKEND_BASE_URL}/health`);
    return handleResponse<HealthStatus>(response);
}

// ==================== EXPORT/IMPORT ====================

export async function exportSources(): Promise<void> {
    const response = await fetchWithTimeout(`${BACKEND_BASE_URL}/api/sources/export`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `news_sources_backup_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

export async function importSources(file: File, mode: 'add' | 'replace' = 'add'): Promise<{ status: string; imported: number; skipped: number; errors: string[] }> {
    const text = await file.text();
    const data = JSON.parse(text);

    const response = await fetchWithTimeout(`${BACKEND_BASE_URL}/api/sources/import?mode=${mode}`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    return handleResponse(response);
}

export async function exportConfig(): Promise<void> {
    const response = await fetchWithTimeout(`${BACKEND_BASE_URL}/api/config/export`);
    const blob = await response.blob();
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `app_config_backup_${new Date().toISOString().replace(/[:.]/g, '-')}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    window.URL.revokeObjectURL(url);
}

export async function importConfig(file: File): Promise<{ status: string; imported: number; errors: string[] }> {
    const text = await file.text();
    const data = JSON.parse(text);

    const response = await fetchWithTimeout(`${BACKEND_BASE_URL}/api/config/import`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(data)
    });

    return handleResponse(response);
}
