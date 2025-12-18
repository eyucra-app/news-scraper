'use client';

import { useEffect, useState, useRef } from 'react';
import {
    getSources,
    createSource,
    updateSource,
    deleteSource,
    testSource,
    exportSources,
    importSources,
} from '@/lib/api';
import type { NewsSource, Category } from '@/lib/types';
import { formatBoliviaTime } from '@/lib/timezone';

const CATEGORIES: Category[] = [
    'local',
    'nacional',
    'mundo',
    'deportes',
    'tecnologia',
    'economia',
    'entretenimiento',
    'otro',
];

export default function SourcesPage() {
    const [sources, setSources] = useState<NewsSource[]>([]);
    const [loading, setLoading] = useState(true);
    const [showForm, setShowForm] = useState(false);
    const [editingSource, setEditingSource] = useState<NewsSource | null>(null);
    const [testResult, setTestResult] = useState('');
    const [deleteConfirm, setDeleteConfirm] = useState<{ show: boolean; id: number | null; name: string }>({
        show: false,
        id: null,
        name: '',
    });
    const [showImportModal, setShowImportModal] = useState(false);
    const [importMode, setImportMode] = useState<'add' | 'replace'>('add');
    const [importMessage, setImportMessage] = useState('');
    const fileInputRef = useRef<HTMLInputElement>(null);

    useEffect(() => {
        loadSources();
    }, []);

    async function loadSources() {
        try {
            const data = await getSources();
            setSources(data);
        } catch (error) {
            console.error('Error loading sources:', error);
        } finally {
            setLoading(false);
        }
    }

    async function handleSave(formData: Partial<NewsSource>) {
        try {
            if (editingSource) {
                await updateSource(editingSource.id, formData);
            } else {
                await createSource(formData);
            }
            setShowForm(false);
            setEditingSource(null);
            loadSources();
        } catch (error: any) {
            alert('Error al guardar: ' + error.message);
        }
    }

    function handleDeleteClick(id: number, name: string) {
        console.log('Opening delete confirmation for:', id, name);
        setDeleteConfirm({ show: true, id, name });
    }

    async function confirmDelete() {
        if (!deleteConfirm.id) return;

        console.log('Deleting source with id:', deleteConfirm.id);
        try {
            await deleteSource(deleteConfirm.id);
            console.log('Delete successful, reloading sources...');
            setDeleteConfirm({ show: false, id: null, name: '' });
            await loadSources();
        } catch (error: any) {
            console.error('Error deleting source:', error);
            alert('Error al eliminar: ' + error.message);
        }
    }

    function cancelDelete() {
        console.log('Delete cancelled');
        setDeleteConfirm({ show: false, id: null, name: '' });
    }

    async function handleTest(id: number) {
        setTestResult('🧪 Probando fuente...');
        try {
            const result = await testSource(id);
            console.log('Test result:', result);
            if (result && result.stats && typeof result.stats.headlines_found !== 'undefined') {
                setTestResult(
                    `✅ Test exitoso: ${result.stats.headlines_found} titulares encontrados (${result.stats.headlines_new} nuevos)`
                );
            } else {
                setTestResult('❌ Error: Respuesta inválida del servidor');
            }
        } catch (error: any) {
            console.error('Test error:', error);
            setTestResult(`❌ Error al probar fuente: ${error.message || 'Error desconocido'}`);
        }
    }


    async function handleExport() {
        try {
            // Obtener datos de las fuentes desde el backend
            const response = await fetch('http://localhost:8000/api/sources/export');
            const jsonData = await response.text();

            // Generar nombre de archivo con timestamp
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, 19);
            const filename = `news_sources_backup_${timestamp}.json`;

            // Usar API nativa si está disponible (pywebview)
            if (window.pywebview) {
                const result = await window.pywebview.api.save_file_dialog(filename, jsonData);
                if (result.success) {
                    setTestResult(`✅ Exportado a: ${result.path}`);
                } else if (result.cancelled) {
                    setTestResult('ℹ️ Exportación cancelada');
                } else {
                    setTestResult(`❌ Error: ${result.error}`);
                }
            } else {
                // Fallback para navegador web (desarrollo)
                const blob = new Blob([jsonData], { type: 'application/json' });
                const url = URL.createObjectURL(blob);
                const a = document.createElement('a');
                a.href = url;
                a.download = filename;
                a.click();
                URL.revokeObjectURL(url);
                setTestResult('📥 Fuentes exportadas');
            }

            setTimeout(() => setTestResult(''), 5000);
        } catch (error: any) {
            setTestResult(`❌ Error al exportar: ${error.message}`);
        }
    }

    async function handleImport(event: React.ChangeEvent<HTMLInputElement>) {
        const file = event.target.files?.[0];
        if (!file) return;

        try {
            setImportMessage('⏳ Importando...');
            const result = await importSources(file, importMode);
            setImportMessage(`✅ Importación completada\n${result.imported} importadas, ${result.skipped} omitidas`);
            await loadSources();
            setTimeout(() => {
                setShowImportModal(false);
                setImportMessage('');
            }, 2000);
        } catch (error: any) {
            setImportMessage(`❌ Error: ${error.message}`);
        }

        // Reset input
        if (fileInputRef.current) {
            fileInputRef.current.value = '';
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-slate-400">Cargando fuentes...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">🌐 Fuentes de Noticias</h1>
                    <p className="text-slate-400">Gestiona las fuentes de donde se extraen los titulares</p>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={handleExport}
                        className="px-4 py-3 bg-emerald-600 hover:bg-emerald-700 text-white rounded-lg font-medium transition flex items-center space-x-2"
                        title="Exportar fuentes"
                    >
                        <span>📥</span>
                        <span className="hidden sm:inline">Exportar</span>
                    </button>
                    <button
                        onClick={() => setShowImportModal(true)}
                        className="px-4 py-3 bg-violet-600 hover:bg-violet-700 text-white rounded-lg font-medium transition flex items-center space-x-2"
                        title="Importar fuentes"
                    >
                        <span>📤</span>
                        <span className="hidden sm:inline">Importar</span>
                    </button>
                    <button
                        onClick={() => {
                            setEditingSource(null);
                            setShowForm(true);
                        }}
                        className="px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition flex items-center space-x-2"
                    >
                        <span>➕</span>
                        <span>Nueva Fuente</span>
                    </button>
                </div>
            </div>

            {/* Import Modal */}
            {showImportModal && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 max-w-md w-full">
                        <h3 className="text-xl font-bold text-white mb-4">📤 Importar Fuentes</h3>

                        <div className="mb-4">
                            <label className="block text-sm font-medium text-slate-300 mb-2">Modo de Importación</label>
                            <select
                                value={importMode}
                                onChange={(e) => setImportMode(e.target.value as 'add' | 'replace')}
                                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-violet-500"
                            >
                                <option value="add">Agregar a existentes</option>
                                <option value="replace">Reemplazar todas</option>
                            </select>
                            <p className="text-xs text-slate-500 mt-1">
                                {importMode === 'add'
                                    ? 'Las fuentes nuevas se agregarán, las existentes se omitirán'
                                    : '⚠️ Se eliminarán todas las fuentes actuales'}
                            </p>
                        </div>

                        <div className="mb-4">
                            <input
                                ref={fileInputRef}
                                type="file"
                                accept=".json"
                                onChange={handleImport}
                                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white file:mr-4 file:py-2 file:px-4 file:rounded file:border-0 file:text-sm file:font-semibold file:bg-violet-600 file:text-white hover:file:bg-violet-700"
                            />
                        </div>

                        {importMessage && (
                            <div className="mb-4 p-3 bg-slate-900/50 rounded-lg text-sm text-slate-300 whitespace-pre-line">
                                {importMessage}
                            </div>
                        )}

                        <div className="flex gap-2">
                            <button
                                onClick={() => {
                                    setShowImportModal(false);
                                    setImportMessage('');
                                }}
                                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition"
                            >
                                Cerrar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Test Result */}
            {testResult && (
                <div className="p-4 bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 text-slate-300">
                    {testResult}
                </div>
            )}

            {/* Delete Confirmation Dialog */}
            {deleteConfirm.show && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 max-w-md w-full">
                        <h3 className="text-xl font-bold text-white mb-4">🗑️ Confirmar Eliminación</h3>
                        <p className="text-slate-300 mb-6">
                            ¿Estás seguro de eliminar la fuente <span className="font-semibold text-white">"{deleteConfirm.name}"</span>?
                            <br />
                            <span className="text-sm text-slate-400 mt-2 block">Esta acción no se puede deshacer.</span>
                        </p>
                        <div className="flex space-x-3">
                            <button
                                onClick={confirmDelete}
                                className="flex-1 px-4 py-2 bg-rose-600 hover:bg-rose-700 text-white rounded-lg font-medium transition"
                            >
                                Sí, Eliminar
                            </button>
                            <button
                                onClick={cancelDelete}
                                className="flex-1 px-4 py-2 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition"
                            >
                                Cancelar
                            </button>
                        </div>
                    </div>
                </div>
            )}

            {/* Form Modal */}
            {showForm && (
                <SourceForm
                    source={editingSource}
                    onSave={handleSave}
                    onCancel={() => {
                        setShowForm(false);
                        setEditingSource(null);
                    }}
                />
            )}

            {/* Sources List */}
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                {sources.map((source) => (
                    <SourceCard
                        key={source.id}
                        source={source}
                        onEdit={() => {
                            setEditingSource(source);
                            setShowForm(true);
                        }}
                        onDelete={() => handleDeleteClick(source.id, source.name)}
                        onTest={() => handleTest(source.id)}
                    />
                ))}
            </div>

            {sources.length === 0 && (
                <div className="text-center py-20 text-slate-400">
                    <div className="text-6xl mb-4">📭</div>
                    <p className="text-xl mb-2">No hay fuentes configuradas</p>
                    <p className="text-sm">Agrega tu primera fuente de noticias para comenzar</p>
                </div>
            )}
        </div>
    );
}

function SourceCard({
    source,
    onEdit,
    onDelete,
    onTest,
}: {
    source: NewsSource;
    onEdit: () => void;
    onDelete: () => void;
    onTest: () => void;
}) {
    return (
        <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6 hover:border-indigo-500/50 transition">
            <div className="flex justify-between items-start mb-4">
                <div>
                    <h3 className="text-xl font-semibold text-white mb-1">{source.name}</h3>
                    <a
                        href={source.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="text-sm text-indigo-400 hover:text-indigo-300"
                    >
                        {source.url.length > 50 ? source.url.substring(0, 50) + '...' : source.url}
                    </a>
                </div>
                <span
                    className={`px-3 py-1 rounded-full text-xs font-medium ${source.is_active
                        ? 'bg-emerald-500/20 text-emerald-400'
                        : 'bg-slate-500/20 text-slate-400'
                        }`}
                >
                    {source.is_active ? '✓ Activa' : '○ Inactiva'}
                </span>
            </div>

            <div className="grid grid-cols-2 gap-4 mb-4 text-sm">
                <div>
                    <p className="text-slate-400">Categoría</p>
                    <p className="text-white font-medium capitalize">{source.category}</p>
                </div>
                <div>
                    <p className="text-slate-400">Scrapes</p>
                    <p className="text-white font-medium">{source.scrape_count}</p>
                </div>
                <div>
                    <p className="text-slate-400">Container</p>
                    <p className="text-white font-mono text-xs truncate">{source.container}</p>
                </div>
                <div>
                    <p className="text-slate-400">Holder</p>
                    <p className="text-white font-mono text-xs truncate">{source.holder}</p>
                </div>
            </div>

            {source.last_scraped_at && (
                <p className="text-xs text-slate-500 mb-4">
                    Último scrape: {formatBoliviaTime(source.last_scraped_at)}
                </p>
            )}

            <div className="flex space-x-2">
                <button
                    onClick={onTest}
                    className="flex-1 px-4 py-2 bg-violet-600/20 hover:bg-violet-600/30 text-violet-400 rounded-lg font-medium transition text-sm"
                >
                    🧪 Probar
                </button>
                <button
                    onClick={onEdit}
                    className="flex-1 px-4 py-2 bg-indigo-600/20 hover:bg-indigo-600/30 text-indigo-400 rounded-lg font-medium transition text-sm"
                >
                    ✏️ Editar
                </button>
                <button
                    onClick={onDelete}
                    className="flex-1 px-4 py-2 bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 rounded-lg font-medium transition text-sm"
                >
                    🗑️ Eliminar
                </button>
            </div>
        </div>
    );
}

function SourceForm({
    source,
    onSave,
    onCancel,
}: {
    source: NewsSource | null;
    onSave: (data: Partial<NewsSource>) => void;
    onCancel: () => void;
}) {
    const [formData, setFormData] = useState<Partial<NewsSource>>(
        source || {
            name: '',
            url: '',
            container: '',
            holder: '',
            data_field: '',
            category: 'mundo',
            is_active: true,
            requires_js: false,
        }
    );

    function handleSubmit(e: React.FormEvent) {
        e.preventDefault();
        onSave(formData);
    }

    return (
        <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
            <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 max-w-2xl w-full max-h-[90vh] overflow-y-auto">
                <h2 className="text-2xl font-bold text-white mb-6">
                    {source ? 'Editar Fuente' : 'Nueva Fuente'}
                </h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Nombre *</label>
                        <input
                            type="text"
                            required
                            value={formData.name}
                            onChange={(e) => setFormData({ ...formData, name: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                            placeholder="Ej: CNN Español"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">URL *</label>
                        <input
                            type="url"
                            required
                            value={formData.url}
                            onChange={(e) => setFormData({ ...formData, url: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                            placeholder="https://sitio.com/noticias"
                        />
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Container (clase CSS) *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.container}
                                onChange={(e) => setFormData({ ...formData, container: e.target.value })}
                                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500 font-mono text-sm"
                                placeholder="news-container"
                            />
                        </div>

                        <div>
                            <label className="block text-sm font-medium text-slate-300 mb-2">
                                Holder (etiqueta HTML) *
                            </label>
                            <input
                                type="text"
                                required
                                value={formData.holder}
                                onChange={(e) => setFormData({ ...formData, holder: e.target.value })}
                                className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500 font-mono text-sm"
                                placeholder="h2"
                            />
                        </div>
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">
                            Data Field (opcional)
                        </label>
                        <input
                            type="text"
                            value={formData.data_field || ''}
                            onChange={(e) => setFormData({ ...formData, data_field: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500 font-mono text-sm"
                            placeholder="subtitle"
                        />
                    </div>

                    <div>
                        <label className="block text-sm font-medium text-slate-300 mb-2">Categoría *</label>
                        <select
                            value={formData.category}
                            onChange={(e) => setFormData({ ...formData, category: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                        >
                            {CATEGORIES.map((cat) => (
                                <option key={cat} value={cat} className="capitalize">
                                    {cat}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                        <div className="flex items-center">
                            <label className="flex items-center space-x-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={formData.is_active}
                                    onChange={(e) => setFormData({ ...formData, is_active: e.target.checked })}
                                    className="w-5 h-5 rounded border-slate-700 bg-slate-900 text-indigo-600 focus:ring-indigo-500"
                                />
                                <span className="text-slate-300">Fuente activa</span>
                            </label>
                        </div>

                        <div className="flex items-center">
                            <label className="flex items-center space-x-3 cursor-pointer">
                                <input
                                    type="checkbox"
                                    checked={formData.requires_js || false}
                                    onChange={(e) => setFormData({ ...formData, requires_js: e.target.checked })}
                                    className="w-5 h-5 rounded border-slate-700 bg-slate-900 text-violet-600 focus:ring-violet-500"
                                />
                                <span className="text-slate-300">🎭 Requiere JavaScript</span>
                            </label>
                        </div>
                    </div>

                    <div className="flex space-x-3 pt-4">
                        <button
                            type="submit"
                            className="flex-1 px-6 py-3 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg font-medium transition"
                        >
                            {source ? 'Actualizar' : 'Crear'} Fuente
                        </button>
                        <button
                            type="button"
                            onClick={onCancel}
                            className="flex-1 px-6 py-3 bg-slate-700 hover:bg-slate-600 text-white rounded-lg font-medium transition"
                        >
                            Cancelar
                        </button>
                    </div>
                </form>
            </div>
        </div>
    );
}
