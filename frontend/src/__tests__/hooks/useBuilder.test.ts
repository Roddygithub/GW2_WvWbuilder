/**
 * Tests for useBuilder hook
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, waitFor } from '@testing-library/react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { useOptimizeComposition, useGameModes, useProfessions } from '../../hooks/useBuilder';
import * as builderApi from '../../api/builder';

// Mock the builder API
vi.mock('../../api/builder');

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>{children}</QueryClientProvider>
  );
};

describe('useOptimizeComposition', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should successfully optimize composition', async () => {
    const mockResponse = {
      composition: {
        id: 1,
        name: 'Optimized WvW Zerg',
        squad_size: 15,
        game_type: 'wvw',
        game_mode: 'zerg',
        members: [
          {
            position: 1,
            profession_id: 1,
            profession_name: 'Guardian',
            elite_spec_id: 27,
            elite_spec_name: 'Firebrand',
            role: 'healer',
          },
        ],
      },
      global_score: 0.85,
      metrics: {
        boon_coverage: {
          quickness: 0.90,
          alacrity: 0.85,
          stability: 0.88,
        },
        role_distribution: {
          healer: 3,
          boon_support: 5,
          dps: 7,
        },
      },
    };

    vi.mocked(builderApi.optimizeComposition).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useOptimizeComposition(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      squad_size: 15,
      game_type: 'wvw',
      game_mode: 'zerg',
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockResponse);
    expect(builderApi.optimizeComposition).toHaveBeenCalledWith({
      squad_size: 15,
      game_type: 'wvw',
      game_mode: 'zerg',
    });
  });

  it('should handle optimization error', async () => {
    const mockError = new Error('Optimization failed');
    vi.mocked(builderApi.optimizeComposition).mockRejectedValue(mockError);

    const { result } = renderHook(() => useOptimizeComposition(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      squad_size: 5,
      game_type: 'pve',
      game_mode: 'fractale',
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBe(mockError);
  });

  it('should optimize with fixed professions', async () => {
    const mockResponse = {
      composition: {
        id: 2,
        name: 'Custom PvE',
        squad_size: 5,
        game_type: 'pve',
        game_mode: 'fractale',
        members: [],
      },
      global_score: 0.80,
      metrics: {},
    };

    vi.mocked(builderApi.optimizeComposition).mockResolvedValue(mockResponse);

    const { result } = renderHook(() => useOptimizeComposition(), {
      wrapper: createWrapper(),
    });

    result.current.mutate({
      squad_size: 5,
      game_type: 'pve',
      game_mode: 'fractale',
      fixed_professions: [1, 1, 2],
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(builderApi.optimizeComposition).toHaveBeenCalledWith({
      squad_size: 5,
      game_type: 'pve',
      game_mode: 'fractale',
      fixed_professions: [1, 1, 2],
    });
  });
});

describe('useGameModes', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch game modes successfully', async () => {
    const mockModes = {
      game_types: {
        wvw: {
          name: 'World vs World',
          modes: [
            {
              id: 'zerg',
              name: 'Zerg',
              description: 'Large scale battles',
              squad_size_range: [30, 50],
              emphasis: ['stability', 'healing', 'boon_uptime'],
            },
            {
              id: 'roaming',
              name: 'Roaming',
              description: 'Small group fights',
              squad_size_range: [3, 10],
              emphasis: ['damage', 'mobility', 'survivability'],
            },
          ],
        },
        pve: {
          name: 'Player vs Environment',
          modes: [
            {
              id: 'fractale',
              name: 'Fractals',
              description: '5-man dungeon content',
              squad_size_range: [5, 5],
              emphasis: ['quickness', 'alacrity', 'damage'],
            },
          ],
        },
      },
    };

    vi.mocked(builderApi.getGameModes).mockResolvedValue(mockModes);

    const { result } = renderHook(() => useGameModes(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockModes);
    expect(builderApi.getGameModes).toHaveBeenCalled();
  });

  it('should handle fetch error', async () => {
    const mockError = new Error('Failed to fetch modes');
    vi.mocked(builderApi.getGameModes).mockRejectedValue(mockError);

    const { result } = renderHook(() => useGameModes(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isError).toBe(true));

    expect(result.current.error).toBe(mockError);
  });
});

describe('useProfessions', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('should fetch professions successfully', async () => {
    const mockProfessions = {
      professions: [
        { id: 1, name: 'Guardian', color: '#72C1D9' },
        { id: 2, name: 'Revenant', color: '#D16E5A' },
        { id: 3, name: 'Necromancer', color: '#52A76F' },
      ],
    };

    vi.mocked(builderApi.getProfessions).mockResolvedValue(mockProfessions);

    const { result } = renderHook(() => useProfessions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    expect(result.current.data).toEqual(mockProfessions);
    expect(result.current.data?.professions).toHaveLength(3);
    expect(builderApi.getProfessions).toHaveBeenCalled();
  });

  it('should cache professions data', async () => {
    const mockProfessions = {
      professions: [{ id: 1, name: 'Guardian', color: '#72C1D9' }],
    };

    vi.mocked(builderApi.getProfessions).mockResolvedValue(mockProfessions);

    const { result, rerender } = renderHook(() => useProfessions(), {
      wrapper: createWrapper(),
    });

    await waitFor(() => expect(result.current.isSuccess).toBe(true));

    // Rerender should use cached data
    rerender();

    // API should only be called once due to caching
    expect(builderApi.getProfessions).toHaveBeenCalledTimes(1);
  });
});
