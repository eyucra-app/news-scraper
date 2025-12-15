'use client';

import { useEffect, useState } from 'react';
import {
    controlTicker,
    getConfig,
    startAutoMode,
    stopAutoMode,
    getAutoModeStatus,
    getTickerState,
    type AutoModeStatus
} from '@/lib/api';
import { ModeToggle, ManualControls, AutoControls } from '@/components/TickerModeComponents';

export default function TickerPage() {
    // Modo de operación: manual o automático
    const [mode, setMode] = useState<'manual' | 'auto'>('manual');

    // Estado modo automático
    const [autoStatus, setAutoStatus] = useState<AutoModeStatus | null>(null);

    // Estados del ticker
    const [tickerState, setTickerState] = useState<'In' | 'Out'>('Out');
    const [category, setCategory] = useState('mundo');
    const [separatorUrl, setSeparatorUrl] = useState('https://assets.singular.live/7072b13f9e20b98034f48d6202400ff9/svgs/7esb5NbN8cQxcCk7X0szej_w24h24.svg');
    const [showSourceName, setShowSourceName] = useState(true);
    const [rotationInterval, setRotationInterval] = useState(60);
    const [schedulerInterval, setSchedulerInterval] = useState(10);
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(false);
    const [outputUrl, setOutputUrl] = useState('');
    const [mounted, setMounted] = useState(false);

    // Inicialización
    useEffect(() => {
        async function initializeState() {
            setMounted(true);

            // Cargar desde localStorage
            const savedMode = localStorage.getItem('ticker_mode');
            const savedCategory = localStorage.getItem('ticker_category');
            const savedTickerState = localStorage.getItem('ticker_state');
            const savedShowSourceName = localStorage.getItem('ticker_show_source_name');
            const savedRotationInterval = localStorage.getItem('ticker_rotation_interval');
            const savedSchedulerInterval = localStorage.getItem('ticker_scheduler_interval');
            const savedSeparatorUrl = localStorage.getItem('ticker_separator_url');

            if (savedMode) setMode(savedMode as 'manual' | 'auto');
            if (savedCategory) setCategory(savedCategory);
            if (savedTickerState) setTickerState(savedTickerState as 'In' | 'Out');
            if (savedShowSourceName) setShowSourceName(savedShowSourceName === 'true');
            if (savedRotationInterval) setRotationInterval(parseInt(savedRotationInterval));
            if (savedSchedulerInterval) setSchedulerInterval(parseInt(savedSchedulerInterval));
            if (savedSeparatorUrl) setSeparatorUrl(savedSeparatorUrl);

            await new Promise(resolve => setTimeout(resolve, 0));
            await loadConfig();

            // Sincronizar estado del ticker con el backend
            try {
                const tickerStateResult = await getTickerState();
                if (tickerStateResult.status === 'success' && tickerStateResult.state) {
                    setTickerState(tickerStateResult.state);
                    console.log(`✅ Estado del ticker sincronizado desde backend: ${tickerStateResult.state}`);
                }
            } catch (error) {
                console.error('⚠️ Error obteniendo estado del ticker:', error);
                // Fallback a localStorage si falla
            }

            // Verificar estado del backend
            try {
                const status = await getAutoModeStatus();
                setAutoStatus(status);

                if (status.auto_mode_active && savedMode !== 'auto') {
                    setMode('auto');
                }
            } catch (error) {
                console.error('Error loading auto mode status:', error);
            }
        }

        initializeState();
    }, []);

    async function loadConfig() {
        try {
            const config = await getConfig();
            if (config.singular.output_url) {
                setOutputUrl(`${config.singular.output_url}?aspect=16:9`);
            }
        } catch (error) {
            console.error('Error loading config:', error);
        }
    }

    // Persistir en localStorage
    useEffect(() => { localStorage.setItem('ticker_mode', mode); }, [mode]);
    useEffect(() => { localStorage.setItem('ticker_category', category); }, [category]);
    useEffect(() => { localStorage.setItem('ticker_state', tickerState); }, [tickerState]);
    useEffect(() => { localStorage.setItem('ticker_show_source_name', String(showSourceName)); }, [showSourceName]);
    useEffect(() => { localStorage.setItem('ticker_rotation_interval', String(rotationInterval)); }, [rotationInterval]);
    useEffect(() => { localStorage.setItem('ticker_scheduler_interval', String(schedulerInterval)); }, [schedulerInterval]);
    useEffect(() => { localStorage.setItem('ticker_separator_url', separatorUrl); }, [separatorUrl]);

    // Handlers modo automático

    async function handleStartAutoMode() {
        if (loading) return;

        setLoading(true);
        setMessage('🚀 Iniciando modo automático...');

        try {
            const result = await startAutoMode(
                rotationInterval,
                schedulerInterval,
                showSourceName
            );

            if (result.status === 'success') {
                setMode('auto');
                setMessage(`✅ ${result.message}`);
                await loadAutoModeStatus();
            } else {
                setMessage(`❌ ${result.message}`);
            }
        } catch (error: any) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }

    async function handleStopAutoMode() {
        if (loading) return;

        setLoading(true);
        setMessage('🛑 Deteniendo modo automático...');

        try {
            const result = await stopAutoMode();

            if (result.status === 'success') {
                setMode('manual');
                setAutoStatus(null);
                setMessage(`✅ ${result.message}`);
            } else {
                setMessage(`❌ ${result.message}`);
            }
        } catch (error: any) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }

    async function loadAutoModeStatus() {
        try {
            const status = await getAutoModeStatus();
            setAutoStatus(status);

            if (status.auto_mode_active && mode === 'manual') {
                setMode('auto');
            }
        } catch (error) {
            console.error('Error loading auto mode status:', error);
        }
    }

    // Polling del estado automático cada 5s
    useEffect(() => {
        if (mode === 'auto') {
            loadAutoModeStatus();
            const interval = setInterval(loadAutoModeStatus, 5000);
            return () => clearInterval(interval);
        }
    }, [mode]);

    // Handlers manuales
    async function handleToggleTicker(newState: 'In' | 'Out') {
        if (loading || mode === 'auto') return;

        setLoading(true);
        setMessage(`${newState === 'In' ? '▶️' : '⏸️'} ${newState === 'In' ? 'Mostrando' : 'Ocultando'} ticker...`);

        try {
            const result = await controlTicker(
                newState,
                category,
                10, // maxHeadlines
                separatorUrl,
                showSourceName,
                false, // autoScrape
                schedulerInterval  // NUEVO - pasar intervalo de scraping
            );

            if (result.status === 'success') {
                setTickerState(newState);
                setMessage(`✅ ${result.message}`);
            } else {
                setMessage(`❌ ${result.message}`);
            }
        } catch (error: any) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setLoading(false);
        }
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-slate-800 to-slate-900 py-0 px-4">
            <div className="max-w-7xl mx-auto space-y-6">
                {/* Header */}
                <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6">
                    <h1 className="text-2xl font-bold text-white mb-2">📺 Control de Ticker</h1>
                    <p className="text-slate-400">Control completo del ticker de noticias en Singular.live</p>
                </div>

                {/* Preview */}
                {outputUrl ? (
                    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-4">
                        {/* Contenedor con altura fija y overflow hidden para recortar */}
                        <div className="relative w-full h-[60px] overflow-hidden rounded-lg border border-slate-600">
                            {/* iframe escalado para mantener proporción 16:9 pero recortado */}
                            <div className="absolute top-0 left-0 w-full" style={{ aspectRatio: '16/9' }}>
                                <iframe
                                    src={outputUrl}
                                    className="w-full h-full border-0"
                                    allow="autoplay"
                                    title="Singular.live Output Preview"
                                />
                            </div>
                        </div>
                        {/* <p className="text-xs text-slate-500 mt-2 text-center">
                            Vista recortada - Solo se muestra el ticker superior
                        </p> */}
                    </div>
                ) : (
                    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-12 text-center">
                        <p className="text-slate-400">
                            ⚠️ Configura tu Control App ID en la página de{' '}
                            <a href="/config" className="text-indigo-400 hover:underline">Configuración</a>
                            {' '}para ver el preview
                        </p>
                    </div>
                )}

                {/* Controls - NUEVO SISTEMA */}
                <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-3">
                    <h2 className="text-lg font-semibold text-white mb-0">🎮 Controles</h2>

                    <ModeToggle
                        mode={mode}
                        onModeChange={(newMode) => {
                            if (newMode === 'auto' && mode === 'manual') {
                                setMode('auto');
                            } else if (newMode === 'manual' && mode === 'auto') {
                                handleStopAutoMode();
                            }
                        }}
                        disabled={loading}
                    />

                    {mode === 'manual' ? (
                        <ManualControls
                            category={category}
                            onCategoryChange={setCategory}
                            tickerState={tickerState}
                            onShowTicker={() => handleToggleTicker('In')}
                            onHideTicker={() => handleToggleTicker('Out')}
                            loading={loading}
                            disabled={false}
                            scrapingInterval={schedulerInterval}
                            onScrapingIntervalChange={setSchedulerInterval}
                        />
                    ) : (
                        <AutoControls
                            autoStatus={autoStatus}
                            onStart={handleStartAutoMode}
                            onStop={handleStopAutoMode}
                            loading={loading}
                            rotationInterval={rotationInterval}
                            scrapingInterval={schedulerInterval}
                            onRotationIntervalChange={setRotationInterval}
                            onScrapingIntervalChange={setSchedulerInterval}
                            disabled={false}
                        />
                    )}

                    <div className="mt-3 p-3 bg-slate-900/50 rounded-lg border border-slate-700">
                        <div className="flex items-center justify-between">
                            <span className="text-sm text-slate-400">Estado del Ticker:</span>
                            <span className={`text-sm font-semibold ${tickerState === 'In' ? 'text-emerald-400' : 'text-slate-500'}`}>
                                {tickerState === 'In' ? '🟢 Visible' : '⚫ Oculto'}
                            </span>
                        </div>
                    </div>

                    <div className="mt-4">
                        <label className="flex items-center justify-between cursor-pointer p-3 bg-slate-900/50 rounded-lg border border-slate-700 hover:border-slate-600 transition">
                            <div>
                                <span className="text-sm font-medium text-slate-300">📰 Mostrar Nombre de Fuente</span>
                                <p className="text-xs text-slate-500 mt-1">
                                    Incluye el nombre de la fuente de noticias en el ticker
                                </p>
                            </div>
                            <div className="relative">
                                <input
                                    type="checkbox"
                                    checked={showSourceName}
                                    onChange={(e) => setShowSourceName(e.target.checked)}
                                    disabled={loading}
                                    className="sr-only peer"
                                />
                                <div className="w-11 h-6 bg-slate-700 peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-slate-300 after:border after:rounded-full after:h-5 after:w-5 after:transition-all peer-checked:bg-emerald-600"></div>
                            </div>
                        </label>
                    </div>

                    {/* Campo de Separador - Disponible en ambos modos */}
                    <div className="mt-4">
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            🔹 URL del Separador
                        </label>
                        <div className="flex gap-2">
                            <input
                                type="text"
                                value={separatorUrl}
                                onChange={(e) => setSeparatorUrl(e.target.value)}
                                placeholder="https://assets.singular.live/..."
                                disabled={loading}
                                className="flex-1 px-3 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white text-sm focus:outline-none focus:border-emerald-500 disabled:opacity-50"
                            />
                            <button
                                onClick={async () => {
                                    setLoading(true);
                                    try {
                                        // Importar la función
                                        const { updateTickerSeparator } = await import('@/lib/api');

                                        // Actualizar solo el separador (endpoint independiente)
                                        const result = await updateTickerSeparator(separatorUrl);

                                        if (result.status === 'success') {
                                            setMessage('✅ ' + result.message);
                                        } else {
                                            setMessage('⚠️ ' + result.message);
                                        }
                                    } catch (error) {
                                        setMessage('❌ Error actualizando separador');
                                    } finally {
                                        setLoading(false);
                                    }
                                }}
                                disabled={loading}
                                className="px-4 py-2 bg-emerald-600 hover:bg-emerald-700 disabled:bg-slate-700 disabled:text-slate-500 text-white text-sm font-medium rounded-lg transition"
                            >
                                Aplicar
                            </button>
                        </div>
                        <p className="text-xs text-slate-500 mt-1">
                            URL del icono que separa los titulares en el ticker
                        </p>
                    </div>
                </div>

                {/* Messages */}
                {message && (
                    <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-4">
                        <p className="text-sm text-slate-300">{message}</p>
                    </div>
                )}
            </div>
        </div>
    );
}
