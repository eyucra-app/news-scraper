// Componente de Toggle Switch para Modo Manual vs Automático
export function ModeToggle({
    mode,
    onModeChange,
    disabled
}: {
    mode: 'manual' | 'auto';
    onModeChange: (mode: 'manual' | 'auto') => void;
    disabled?: boolean;
}) {
    return (
        <div className="flex items-center justify-center space-x-3 mb-6">
            <button
                onClick={() => onModeChange('manual')}
                disabled={disabled}
                className={`px-6 py-2 rounded-l-lg font-medium transition-all ${mode === 'manual'
                    ? 'bg-red-600 text-white shadow-lg'
                    : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                    } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
                🔴 Manual
            </button>
            <button
                onClick={() => onModeChange('auto')}
                disabled={disabled}
                className={`px-6 py-2 rounded-r-lg font-medium transition-all ${mode === 'auto'
                    ? 'bg-green-600 text-white shadow-lg'
                    : 'bg-slate-700 text-slate-400 hover:bg-slate-600'
                    } ${disabled ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'}`}
            >
                🟢 Automático
            </button>
        </div>
    );
}

// Componente de Controles Manuales
export function ManualControls({
    category,
    onCategoryChange,
    tickerState,
    onShowTicker,
    onHideTicker,
    loading,
    disabled,
    scrapingInterval,
    onScrapingIntervalChange
}: {
    category: string;
    onCategoryChange: (category: string) => void;
    tickerState: 'In' | 'Out';
    onShowTicker: () => void;
    onHideTicker: () => void;
    loading: boolean;
    disabled: boolean;
    scrapingInterval: number;
    onScrapingIntervalChange: (value: number) => void;
}) {
    return (
        <div className="space-y-4">
            <div>
                <label className="block text-sm font-medium text-slate-300 mb-2">
                    Categoría
                </label>
                <select
                    value={category}
                    onChange={(e) => onCategoryChange(e.target.value)}
                    disabled={disabled || loading}
                    className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
                >
                    <option value="local">📍 Local</option>
                    <option value="nacional">🇧🇴 Nacional</option>
                    <option value="mundo">🌎 Mundo</option>
                    <option value="deportes">⚽ Deportes</option>
                    <option value="economia">💰 Economía</option>
                    <option value="tecnologia">💻 Tecnología</option>
                    <option value="entretenimiento">🎬 Entretenimiento</option>
                </select>
            </div>

            {/* Configuración de Scraping Automático */}
            <div className="p-3 bg-slate-900/50 rounded-lg border border-slate-700">
                <label className="block text-sm font-medium text-slate-300 mb-2">
                    🔄 Intervalo de Scraping (minutos)
                </label>
                <input
                    type="number"
                    value={scrapingInterval}
                    onChange={(e) => onScrapingIntervalChange(parseInt(e.target.value) || 10)}
                    min="1"
                    max="60"
                    disabled={disabled || loading}
                    className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-blue-500 disabled:opacity-50"
                />
                <p className="text-xs text-slate-500 mt-1">
                    El scraping se ejecutará automáticamente mientras el ticker esté visible
                </p>
            </div>

            <div className="flex space-x-3">
                <button
                    onClick={onShowTicker}
                    disabled={tickerState === 'In' || loading || disabled}
                    className="flex-1 px-6 py-3 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition flex items-center justify-center space-x-2"
                >
                    <span>▶️</span>
                    <span>Mostrar</span>
                </button>

                <button
                    onClick={onHideTicker}
                    disabled={tickerState === 'Out' || loading || disabled}
                    className="flex-1 px-6 py-3 bg-rose-600 hover:bg-rose-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition flex items-center justify-center space-x-2"
                >
                    <span>⏸️</span>
                    <span>Ocultar</span>
                </button>
            </div>
        </div>
    );
}

// Componente de Controles Automáticos
export function AutoControls({
    autoStatus,
    onStart,
    onStop,
    loading,
    rotationInterval,
    scrapingInterval,
    onRotationIntervalChange,
    onScrapingIntervalChange,
    disabled
}: {
    autoStatus: any | null;
    onStart: () => void;
    onStop: () => void;
    loading: boolean;
    rotationInterval: number;
    scrapingInterval: number;
    onRotationIntervalChange: (value: number) => void;
    onScrapingIntervalChange: (value: number) => void;
    disabled: boolean;
}) {
    const isActive = autoStatus?.auto_mode_active;

    if (!isActive) {
        // Modo automático NO activo - Mostrar configuración e iniciar
        return (
            <div className="space-y-4">
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-xs text-slate-400 mb-2">
                            Rotación (segundos):
                        </label>
                        <input
                            type="number"
                            value={rotationInterval}
                            onChange={(e) => onRotationIntervalChange(parseInt(e.target.value) || 60)}
                            min="10"
                            max="300"
                            disabled={disabled || loading}
                            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-green-500 disabled:opacity-50"
                        />
                    </div>
                    <div>
                        <label className="block text-xs text-slate-400 mb-2">
                            Scraping (minutos):
                        </label>
                        <input
                            type="number"
                            value={scrapingInterval}
                            onChange={(e) => onScrapingIntervalChange(parseInt(e.target.value) || 10)}
                            min="1"
                            max="60"
                            disabled={disabled || loading}
                            className="w-full px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-green-500 disabled:opacity-50"
                        />
                    </div>
                </div>

                <button
                    onClick={onStart}
                    disabled={disabled || loading}
                    className="w-full px-6 py-4 bg-gradient-to-r from-green-600 to-emerald-600 hover:from-green-700 hover:to-emerald-700 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white rounded-lg font-bold transition flex items-center justify-center space-x-2"
                >
                    <span>🚀</span>
                    <span>Iniciar Modo Automático</span>
                </button>
            </div>
        );
    }

    // Modo automático ACTIVO - Mostrar estado y detener
    return (
        <div className="space-y-4">
            <div className="bg-green-900/30 border border-green-700 rounded-lg p-4 space-y-3">
                <div className="flex items-center space-x-2">
                    <span className="flex h-3 w-3">
                        <span className="animate-ping absolute inline-flex h-3 w-3 rounded-full bg-green-400 opacity-75"></span>
                        <span className="relative inline-flex rounded-full h-3 w-3 bg-green-500"></span>
                    </span>
                    <span className="text-sm font-medium text-green-400">
                        MODO AUTOMÁTICO ACTIVO
                    </span>
                </div>

                <div className="space-y-2 text-sm">
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400">Categoría Actual:</span>
                        <span className="text-white font-medium">
                            🔄 {autoStatus.current_category?.toUpperCase() || 'LOCAL'}
                        </span>
                    </div>
                    {autoStatus.next_rotation_in && (
                        <div className="flex justify-between items-center">
                            <span className="text-slate-400">Siguiente rotación:</span>
                            <span className="text-green-400 font-mono">
                                {autoStatus.next_rotation_in}s
                            </span>
                        </div>
                    )}
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400">Intervalo rotación:</span>
                        <span className="text-white">{autoStatus.rotation_interval_seconds}s</span>
                    </div>
                    <div className="flex justify-between items-center">
                        <span className="text-slate-400">Intervalo scraping:</span>
                        <span className="text-white">{autoStatus.scraping_interval_minutes}min</span>
                    </div>
                </div>
            </div>

            <button
                onClick={onStop}
                disabled={disabled || loading}
                className="w-full px-6 py-4 bg-gradient-to-r from-red-600 to-rose-600 hover:from-red-700 hover:to-rose-700 disabled:from-slate-700 disabled:to-slate-700 disabled:text-slate-500 text-white rounded-lg font-bold transition flex items-center justify-center space-x-2"
            >
                <span>🛑</span>
                <span>Detener Todo</span>
            </button>
        </div>
    );
}
