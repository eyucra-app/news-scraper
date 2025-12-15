'use client';

import { useEffect, useState } from 'react';
import {
    getHeadlines,
    getSources,
    deleteHeadline,
} from '@/lib/api';
import type { Headline, NewsSource } from '@/lib/types';
import { formatBoliviaTime } from '@/lib/timezone';

export default function HeadlinesPage() {
    const [headlines, setHeadlines] = useState<Headline[]>([]);
    const [sources, setSources] = useState<NewsSource[]>([]);
    const [loading, setLoading] = useState(true);
    const [selectedIds, setSelectedIds] = useState<number[]>([]);
    const [filters, setFilters] = useState({
        category: '',
        sourceId: '',
        unsentOnly: false,
    });
    const [message, setMessage] = useState('');
    const [deleteConfirm, setDeleteConfirm] = useState<{
        show: boolean;
        id: number | null;
        type: 'single' | 'multiple';
        count: number;
    }>({
        show: false,
        id: null,
        type: 'single',
        count: 0,
    });

    useEffect(() => {
        loadData();
    }, [filters]);

    async function loadData() {
        try {
            const [headlinesData, sourcesData] = await Promise.all([
                getHeadlines({
                    limit: 50,
                    category: filters.category || undefined,
                    sourceId: filters.sourceId ? Number(filters.sourceId) : undefined,
                    unsentOnly: filters.unsentOnly,
                }),
                getSources(),
            ]);
            setHeadlines(headlinesData);
            setSources(sourcesData);
        } catch (error) {
            console.error('Error loading headlines:', error);
        } finally {
            setLoading(false);
        }
    }



    function handleDeleteClick(id: number) {
        setDeleteConfirm({ show: true, id, type: 'single', count: 1 });
    }

    function handleDeleteSelectedClick() {
        if (selectedIds.length === 0) {
            alert('Selecciona al menos un titular');
            return;
        }
        setDeleteConfirm({
            show: true,
            id: null,
            type: 'multiple',
            count: selectedIds.length,
        });
    }

    async function confirmDelete() {
        try {
            if (deleteConfirm.type === 'single' && deleteConfirm.id) {
                await deleteHeadline(deleteConfirm.id);
                setMessage('✅ Titular eliminado');
            } else if (deleteConfirm.type === 'multiple') {
                // Eliminar múltiples
                await Promise.all(selectedIds.map((id) => deleteHeadline(id)));
                setMessage(`✅ ${selectedIds.length} titulares eliminados`);
                setSelectedIds([]);
            }
            setDeleteConfirm({ show: false, id: null, type: 'single', count: 0 });
            loadData();
        } catch (error: any) {
            setMessage(`❌ Error: ${error.message}`);
        }
    }

    function cancelDelete() {
        setDeleteConfirm({ show: false, id: null, type: 'single', count: 0 });
    }

    function toggleSelection(id: number) {
        setSelectedIds((prev) =>
            prev.includes(id) ? prev.filter((i) => i !== id) : [...prev, id]
        );
    }

    function toggleAll() {
        if (selectedIds.length === headlines.length) {
            setSelectedIds([]);
        } else {
            setSelectedIds(headlines.map((h) => h.id));
        }
    }

    if (loading) {
        return (
            <div className="flex items-center justify-center h-96">
                <div className="text-center">
                    <div className="w-16 h-16 border-4 border-indigo-500 border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
                    <p className="text-slate-400">Cargando titulares...</p>
                </div>
            </div>
        );
    }

    return (
        <div className="space-y-6">
            {/* Header */}
            <div className="flex justify-between items-center">
                <div>
                    <h1 className="text-3xl font-bold text-white mb-2">📜 Titulares</h1>
                    <p className="text-slate-400">
                        {headlines.length} titulares · {selectedIds.length} seleccionados
                    </p>
                </div>
                <button
                    onClick={handleDeleteSelectedClick}
                    disabled={selectedIds.length === 0}
                    className="px-6 py-3 bg-rose-600 hover:bg-rose-700 disabled:bg-slate-700 disabled:text-slate-500 text-white rounded-lg font-medium transition flex items-center space-x-2"
                >
                    <span>🗑️</span>
                    <span>Eliminar ({selectedIds.length})</span>
                </button>
            </div>

            {/* Message */}
            {message && (
                <div className="p-4 bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 text-slate-300">
                    {message}
                </div>
            )}

            {/* Delete Confirmation Dialog */}
            {deleteConfirm.show && (
                <div className="fixed inset-0 bg-black/50 backdrop-blur-sm flex items-center justify-center z-50 p-4">
                    <div className="bg-slate-800 rounded-xl border border-slate-700 p-6 max-w-md w-full">
                        <h3 className="text-xl font-bold text-white mb-4">🗑️ Confirmar Eliminación</h3>
                        <p className="text-slate-300 mb-6">
                            ¿Estás seguro de eliminar{' '}
                            {deleteConfirm.type === 'single' ? (
                                <span className="font-semibold text-white">este titular</span>
                            ) : (
                                <span className="font-semibold text-white">
                                    {deleteConfirm.count} titulares seleccionados
                                </span>
                            )}
                            ?
                            <br />
                            <span className="text-sm text-slate-400 mt-2 block">
                                Esta acción no se puede deshacer.
                            </span>
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

            {/* Filters */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 p-6">
                <h2 className="text-lg font-semibold text-white mb-4">🔍 Filtros</h2>
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                    <div>
                        <label className="block text-sm text-slate-400 mb-2">Categoría</label>
                        <select
                            value={filters.category}
                            onChange={(e) => setFilters({ ...filters, category: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                        >
                            <option value="">Todas</option>
                            <option value="local">Local</option>
                            <option value="nacional">Nacional</option>
                            <option value="mundo">Mundo</option>
                            <option value="deportes">Deportes</option>
                            <option value="tecnologia">Tecnología</option>
                            <option value="economia">Economía</option>
                            <option value="entretenimiento">Entretenimiento</option>
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-slate-400 mb-2">Fuente</label>
                        <select
                            value={filters.sourceId}
                            onChange={(e) => setFilters({ ...filters, sourceId: e.target.value })}
                            className="w-full px-4 py-2 bg-slate-900 border border-slate-700 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                        >
                            <option value="">Todas</option>
                            {sources.map((s) => (
                                <option key={s.id} value={s.id}>
                                    {s.name}
                                </option>
                            ))}
                        </select>
                    </div>

                    <div>
                        <label className="block text-sm text-slate-400 mb-2">Estado</label>
                        <label className="flex items-center space-x-3 cursor-pointer px-4 py-2">
                            <input
                                type="checkbox"
                                checked={filters.unsentOnly}
                                onChange={(e) => setFilters({ ...filters, unsentOnly: e.target.checked })}
                                className="w-5 h-5 rounded border-slate-700 bg-slate-900 text-indigo-600"
                            />
                            <span className="text-white">Solo pendientes</span>
                        </label>
                    </div>
                </div>
            </div>

            {/* Headlines Table */}
            <div className="bg-slate-800/50 backdrop-blur-lg rounded-xl border border-slate-700 overflow-hidden">
                {headlines.length === 0 ? (
                    <div className="text-center py-20 text-slate-400">
                        <div className="text-6xl mb-4">📭</div>
                        <p className="text-xl">No hay titulares con estos filtros</p>
                    </div>
                ) : (
                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead className="bg-slate-900/50">
                                <tr>
                                    <th className="p-4 text-left">
                                        <input
                                            type="checkbox"
                                            checked={selectedIds.length === headlines.length && headlines.length > 0}
                                            onChange={toggleAll}
                                            className="w-5 h-5 rounded border-slate-700 bg-slate-900 text-indigo-600"
                                        />
                                    </th>
                                    <th className="p-4 text-left text-sm font-medium text-slate-400">Titular</th>
                                    <th className="p-4 text-left text-sm font-medium text-slate-400">Fuente</th>
                                    <th className="p-4 text-left text-sm font-medium text-slate-400">Categoría</th>
                                    <th className="p-4 text-left text-sm font-medium text-slate-400">Estado</th>
                                    <th className="p-4 text-left text-sm font-medium text-slate-400">Fecha</th>
                                    <th className="p-4 text-left text-sm font-medium text-slate-400">Acciones</th>
                                </tr>
                            </thead>
                            <tbody>
                                {headlines.map((headline) => (
                                    <tr
                                        key={headline.id}
                                        className="border-t border-slate-700/50 hover:bg-slate-700/30 transition"
                                    >
                                        <td className="p-4">
                                            <input
                                                type="checkbox"
                                                checked={selectedIds.includes(headline.id)}
                                                onChange={() => toggleSelection(headline.id)}
                                                className="w-5 h-5 rounded border-slate-700 bg-slate-900 text-indigo-600"
                                            />
                                        </td>
                                        <td className="p-4 text-slate-300 max-w-md">
                                            <p className="line-clamp-2">{headline.title}</p>
                                        </td>
                                        <td className="p-4 text-slate-400 text-sm">{headline.source_name}</td>
                                        <td className="p-4">
                                            <span className="px-2 py-1 bg-indigo-500/20 text-indigo-400 rounded text-xs capitalize">
                                                {headline.category}
                                            </span>
                                        </td>
                                        <td className="p-4">
                                            {headline.sent_to_singular ? (
                                                <span className="px-2 py-1 bg-emerald-500/20 text-emerald-400 rounded-full text-xs inline-flex items-center space-x-1">
                                                    <span>✓</span>
                                                    <span>Enviado</span>
                                                </span>
                                            ) : (
                                                <span className="px-2 py-1 bg-amber-500/20 text-amber-400 rounded-full text-xs inline-flex items-center space-x-1">
                                                    <span>⏳</span>
                                                    <span>Pendiente</span>
                                                </span>
                                            )}
                                        </td>
                                        <td className="p-4 text-slate-400 text-sm whitespace-nowrap">
                                            {formatBoliviaTime(headline.created_at, {
                                                month: 'short',
                                                day: 'numeric',
                                                hour: '2-digit',
                                                minute: '2-digit',
                                                second: undefined,
                                            })}
                                        </td>
                                        <td className="p-4">
                                            <button
                                                onClick={() => handleDeleteClick(headline.id)}
                                                className="px-3 py-1 bg-rose-600/20 hover:bg-rose-600/30 text-rose-400 rounded text-xs transition"
                                            >
                                                🗑️
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                )}
            </div>
        </div>
    );
}
