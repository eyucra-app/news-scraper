'use client';

import { useEffect, useState } from 'react';
import { checkBackendAvailability } from '@/lib/api';

export default function BackendStatus() {
    const [isOnline, setIsOnline] = useState<boolean | null>(null);
    const [isChecking, setIsChecking] = useState(true);

    useEffect(() => {
        const checkStatus = async () => {
            setIsChecking(true);
            const available = await checkBackendAvailability();
            setIsOnline(available);
            setIsChecking(false);
        };

        // Check al montar
        checkStatus();

        // Check cada 10 segundos
        const interval = setInterval(checkStatus, 10000);

        return () => clearInterval(interval);
    }, []);

    if (isChecking && isOnline === null) {
        return (
            <div className="fixed top-4 right-4 bg-yellow-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50">
                <div className="w-2 h-2 bg-white rounded-full animate-pulse"></div>
                <span className="text-sm font-medium">Verificando backend...</span>
            </div>
        );
    }

    if (!isOnline) {
        return (
            <div className="fixed top-4 right-4 bg-red-500 text-white px-4 py-3 rounded-lg shadow-lg z-50 max-w-md">
                <div className="flex items-start gap-3">
                    <div className="w-2 h-2 bg-white rounded-full mt-1.5"></div>
                    <div>
                        <h3 className="font-semibold mb-1">Backend no disponible</h3>
                        <p className="text-sm opacity-90 mb-2">
                            El backend local no está ejecutándose. Por favor, inicia la aplicación de backend.
                        </p>
                        <div className="text-xs opacity-75 space-y-1">
                            <p><strong>Windows:</strong> Ejecuta NewsScraperBackend.exe</p>
                            <p><strong>macOS/Linux:</strong> Ejecuta la aplicación desde el instalador</p>
                        </div>
                    </div>
                </div>
            </div>
        );
    }

    return (
        <div className="fixed top-4 right-4 bg-green-500 text-white px-4 py-2 rounded-lg shadow-lg flex items-center gap-2 z-50">
            <div className="w-2 h-2 bg-white rounded-full"></div>
            <span className="text-sm font-medium">Backend conectado</span>
        </div>
    );
}
