'use client';

import { useEffect, useState } from 'react';
import { getConfig, updateSingularConfig, testSingularConnection } from '@/lib/api';

export default function ConfigPage() {
    const [controlAppId, setControlAppId] = useState('');
    const [currentConfig, setCurrentConfig] = useState<any>(null);
    const [message, setMessage] = useState('');
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [testing, setTesting] = useState(false);

    useEffect(() => {
        loadConfig();
    }, []);

    async function loadConfig() {
        try {
            const config = await getConfig();
            setCurrentConfig(config);
            setControlAppId(config.singular.control_app_id || '');
        } catch (error) {
            console.error('Error loading config:', error);
        } finally {
            setLoading(false);
        }
    }

    async function handleSave(e: React.FormEvent) {
        e.preventDefault();

        if (!controlAppId) {
            setMessage('❌ Por favor ingresa el Control App ID');
            return;
        }

        setSaving(true);
        setMessage('💾 Guardando configuración...');

        try {
            const result = await updateSingularConfig(controlAppId);

            if (result.status === 'success') {
                setMessage(`✅ ${result.message}`);
                loadConfig(); // Recargar config
            } else if (result.status === 'warning') {
                setMessage(`⚠️ ${result.message}`);
            } else {
                setMessage(`❌ ${result.message}`);
            }
        } catch (error: any) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setSaving(false);
        }
    }

    async function handleTest() {
        setTesting(true);
        setMessage('🧪 Probando conexión con Singular.live...');

        try {
            const result = await testSingularConnection();

            if (result.status === 'success') {
                setMessage(`✅ ${result.message}`);
            } else {
                setMessage(`❌ ${result.message}`);
            }
        } catch (error: any) {
            setMessage(`❌ Error: ${error.message}`);
        } finally {
            setTesting(false);
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-slate-400">Cargando configuración...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div>
                <h1 className="text-3xl font-bold text-white mb-2">⚙️ Configuración</h1>
                <p className="text-slate-400">Gestiona las credenciales de Singular.live y otras configuraciones</p>
            </div>

            {/* Message */}
            {message && (
                <div className="p-4 bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 text-slate-300">
                    {message}
                </div>
            )}

            {/* Singular.live Configuration */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6">
                <h2 className="text-xl font-bold text-white mb-2">📡 Singular.live</h2>
                <p className="text-slate-400 mb-6">Configura las credenciales para enviar titulares a Singular.live</p>

                {/* Current Status */}
                {currentConfig && (
                    <div className="mb-6 p-4 bg-slate-900/50 rounded-lg border border-slate-700">
                        <div className="space-y-3">
                            <div className="flex items-center justify-between">
                                <div>
                                    <p className="text-sm text-slate-400">Estado actual</p>
                                    <p className="text-white font-medium">
                                        {currentConfig.singular.has_config ? (
                                            <span className="text-emerald-400">✓ Configurado</span>
                                        ) : (
                                            <span className="text-amber-400">⚠ No configurado</span>
                                        )}
                                    </p>
                                </div>
                                <button
                                    onClick={handleTest}
                                    disabled={!currentConfig.singular.has_config || testing}
                                    className="px-4 py-2 bg-violet-600/20 hover:bg-violet-600/30 disabled:bg-slate-700 disabled:text-slate-500 text-violet-400 rounded-lg font-medium transition text-sm"
                                >
                                    {testing ? '🧪 Probando...' : '🧪 Probar Conexión'}
                                </button>
                            </div>

                            {/* Output URL si está configurado */}
                            {currentConfig.singular.output_url && (
                                <div className="pt-3 border-t border-slate-700">
                                    <p className="text-xs text-slate-400 mb-1">Output URL</p>
                                    <p className="text-xs text-slate-300 font-mono truncate">
                                        {currentConfig.singular.output_url}
                                    </p>
                                </div>
                            )}
                        </div>
                    </div>
                )}

                {/* Configuration Form */}
                <form onSubmit={handleSave} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Control App ID *
                        </label>
                        <input
                            type="text"
                            required
                            value={controlAppId}
                            onChange={(e) => setControlAppId(e.target.value)}
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500 font-mono text-sm"
                            placeholder="2hOwhs3lsnaEG4SfcJABP8"
                        />
                        <p className="text-xs text-slate-500 mt-1">
                            Encuéntralo en la URL de tu Control App: /apiv2/controlapps/<strong className="text-indigo-400">[ID]</strong>
                        </p>
                    </div>

                    <button
                        type="submit"
                        disabled={saving}
                        className="w-full px-6 py-3 bg-indigo-600 hover:bg-indigo-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition"
                    >
                        {saving ? '💾 Guardando...' : '💾 Guardar Configuración'}
                    </button>
                </form>
            </div>

            {/* Help Section */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6">
                <h2 className="text-xl font-bold text-white mb-4">📚 Guía de Configuración</h2>

                <div className="space-y-4 text-slate-300 text-sm">
                    <div>
                        <h3 className="font-semibold text-white mb-2">1. Obtener App Instance ID</h3>
                        <p className="text-slate-400 mb-2">El App Instance ID está en la URL del output de tu composition:</p>
                        <code className="block p-3 bg-slate-900 rounded text-xs overflow-x-auto">
                            https://app.singular.live/output/<span className="text-indigo-400 font-bold">0fulrmFKpOyR1tfZSSAQNa</span>
                        </code>
                        <p className="text-slate-500 mt-2">En este ejemplo, el App Instance ID es: <span className="text-indigo-400 font-mono">0fulrmFKpOyR1tfZSSAQNa</span></p>
                    </div>

                    <div>
                        <h3 className="font-semibold text-white mb-2">2. Obtener Shared Token</h3>
                        <ol className="list-decimal list-inside space-y-1 text-slate-400">
                            <li>Ve a Singular.live → Project Settings</li>
                            <li>Navega a la sección "App Shared Tokens"</li>
                            <li>Copia el token (string largo alfanumérico)</li>
                            <li>Pégalo en el campo "Shared Token"</li>
                        </ol>
                    </div>

                    <div>
                        <h3 className="font-semibold text-white mb-2">3. Verificar Conexión</h3>
                        <p className="text-slate-400">
                            Después de guardar, usa el botón "🧪 Probar Conexión" para verificar que las credenciales sean correctas.
                        </p>
                    </div>

                    <div className="p-4 bg-amber-500/10 border border-amber-500/30 rounded-lg">
                        <p className="text-amber-400 font-semibold mb-1">⚠️ Importante</p>
                        <p className="text-slate-400">
                            Los titulares solo se enviarán si las credenciales están configuradas correctamente.
                            Prueba la conexión antes de enviar titulares en producción.
                        </p>
                    </div>
                </div>
            </div>

            {/* Other Settings */}
            {currentConfig && (
                <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6">
                    <h2 className="text-xl font-bold text-white mb-4">🔧 Configuración del Sistema</h2>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                        <div>
                            <p className="text-slate-400">Intervalo de Scraping</p>
                            <p className="text-white font-medium">{currentConfig.scraping_interval} minutos</p>
                        </div>
                        <div>
                            <p className="text-slate-400">Entorno</p>
                            <p className="text-white font-medium capitalize">{currentConfig.environment}</p>
                        </div>
                        <div>
                            <p className="text-slate-400">Modo Debug</p>
                            <p className="text-white font-medium">{currentConfig.debug ? 'Activado' : 'Desactivado'}</p>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
