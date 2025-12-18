// Tipos para la API de pywebview
interface PywebviewAPI {
    save_file_dialog(filename: string, content: string): Promise<{
        success: boolean;
        path?: string;
        cancelled?: boolean;
        error?: string;
    }>;
    open_file_dialog(): Promise<{
        success: boolean;
        content?: string;
        path?: string;
        cancelled?: boolean;
        error?: string;
    }>;
}

interface Pywebview {
    api: PywebviewAPI;
}

declare global {
    interface Window {
        pywebview?: Pywebview;
    }
}

export { };
