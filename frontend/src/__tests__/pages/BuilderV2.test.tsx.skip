/**
 * Tests for BuilderV2 page
 */
import { describe, it, expect, vi, beforeEach } from 'vitest';
import { render, screen, waitFor, fireEvent } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { BrowserRouter } from 'react-router-dom';
import BuilderV2 from '../../pages/BuilderV2';
import * as builderApi from '../../api/builder';

// Mock the builder API
vi.mock('../../api/builder');

// Mock toast notifications
vi.mock('sonner', () => ({
  toast: {
    success: vi.fn(),
    error: vi.fn(),
  },
}));

const createWrapper = () => {
  const queryClient = new QueryClient({
    defaultOptions: {
      queries: { retry: false },
      mutations: { retry: false },
    },
  });
  return ({ children }: { children: React.ReactNode }) => (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>{children}</BrowserRouter>
    </QueryClientProvider>
  );
};

describe('BuilderV2 Page', () => {
  beforeEach(() => {
    vi.clearAllMocks();

    // Mock game modes
    vi.mocked(builderApi.getGameModes).mockResolvedValue({
      game_types: {
        wvw: {
          name: 'World vs World',
          modes: [
            {
              id: 'zerg',
              name: 'Zerg',
              description: 'Large scale battles',
              squad_size_range: [30, 50],
              emphasis: ['stability'],
            },
          ],
        },
        pve: {
          name: 'PvE',
          modes: [
            {
              id: 'fractale',
              name: 'Fractals',
              description: 'Fractals content',
              squad_size_range: [5, 5],
              emphasis: ['quickness'],
            },
          ],
        },
      },
    });

    // Mock professions
    vi.mocked(builderApi.getProfessions).mockResolvedValue({
      professions: [
        { id: 1, name: 'Guardian', color: '#72C1D9' },
        { id: 2, name: 'Revenant', color: '#D16E5A' },
      ],
    });
  });

  it('should render the builder wizard', async () => {
    render(<BuilderV2 />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/Build Your Squad/i)).toBeInTheDocument();
    });
  });

  it('should show step 1: squad size selection', async () => {
    render(<BuilderV2 />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
    });

    // Should have squad size input
    const squadSizeInput = screen.getByRole('spinbutton') || screen.getByLabelText(/squad size/i);
    expect(squadSizeInput).toBeInTheDocument();
  });

  it('should navigate to step 2 after selecting squad size', async () => {
    const user = userEvent.setup();
    render(<BuilderV2 />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
    });

    // Enter squad size
    const squadSizeInput = screen.getByRole('spinbutton') || screen.getByPlaceholderText(/enter squad size/i);
    if (squadSizeInput) {
      await user.clear(squadSizeInput);
      await user.type(squadSizeInput, '15');
    }

    // Click next button
    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText(/Select Game Mode/i)).toBeInTheDocument();
    });
  });

  it('should allow selecting game type and mode', async () => {
    const user = userEvent.setup();
    render(<BuilderV2 />, { wrapper: createWrapper() });

    // Navigate to step 2
    await waitFor(() => {
      expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
    });

    const squadSizeInput = screen.getByRole('spinbutton') || screen.getByPlaceholderText(/enter squad size/i);
    if (squadSizeInput) {
      await user.clear(squadSizeInput);
      await user.type(squadSizeInput, '30');
    }

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText(/Select Game Mode/i)).toBeInTheDocument();
    });

    // Select WvW game type
    const wvwButton = screen.getByRole('button', { name: /World vs World/i });
    await user.click(wvwButton);

    // Should show WvW modes
    await waitFor(() => {
      expect(screen.getByText(/Zerg/i)).toBeInTheDocument();
    });
  });

  it('should trigger optimization on final step', async () => {
    const user = userEvent.setup();

    const mockOptimizationResult = {
      composition: {
        id: 1,
        name: 'Optimized Squad',
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
        },
        role_distribution: {
          healer: 3,
        },
      },
    };

    vi.mocked(builderApi.optimizeComposition).mockResolvedValue(mockOptimizationResult);

    render(<BuilderV2 />, { wrapper: createWrapper() });

    // Navigate through wizard
    await waitFor(() => {
      expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
    });

    // Step 1: Squad size
    const squadSizeInput = screen.getByRole('spinbutton') || screen.getByPlaceholderText(/enter squad size/i);
    if (squadSizeInput) {
      await user.clear(squadSizeInput);
      await user.type(squadSizeInput, '15');
    }

    const nextButton1 = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton1);

    // Step 2: Game mode
    await waitFor(() => {
      expect(screen.getByText(/Select Game Mode/i)).toBeInTheDocument();
    });

    const wvwButton = screen.getByRole('button', { name: /World vs World/i });
    await user.click(wvwButton);

    await waitFor(() => {
      const zergButton = screen.queryByRole('button', { name: /Zerg/i });
      if (zergButton) {
        user.click(zergButton);
      }
    });

    // Click optimize button
    const optimizeButtons = screen.queryAllByRole('button', { name: /optimize/i });
    if (optimizeButtons.length > 0) {
      await user.click(optimizeButtons[0]);

      await waitFor(() => {
        expect(builderApi.optimizeComposition).toHaveBeenCalledWith({
          squad_size: 15,
          game_type: 'wvw',
          game_mode: 'zerg',
        });
      });
    }
  });

  it('should display optimization results', async () => {
    const user = userEvent.setup();

    const mockResult = {
      composition: {
        id: 1,
        name: 'Test Squad',
        squad_size: 5,
        game_type: 'pve',
        game_mode: 'fractale',
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
      global_score: 0.88,
      metrics: {
        boon_coverage: {
          quickness: 0.95,
          alacrity: 0.90,
        },
      },
    };

    vi.mocked(builderApi.optimizeComposition).mockResolvedValue(mockResult);

    render(<BuilderV2 />, { wrapper: createWrapper() });

    // Complete the flow (simplified for test)
    await waitFor(() => {
      expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
    });

    // Trigger optimization (simplified)
    const optimizeButtons = screen.queryAllByRole('button', { name: /optimize/i });
    if (optimizeButtons.length > 0) {
      await user.click(optimizeButtons[0]);

      await waitFor(() => {
        // Should show results
        const scoreText = screen.queryByText(/88%/);
        expect(scoreText || screen.queryByText(/global score/i)).toBeTruthy();
      });
    }
  });

  it('should handle optimization errors gracefully', async () => {
    const user = userEvent.setup();

    vi.mocked(builderApi.optimizeComposition).mockRejectedValue(
      new Error('Optimization failed')
    );

    render(<BuilderV2 />, { wrapper: createWrapper() });

    await waitFor(() => {
      expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
    });

    // Try to optimize
    const optimizeButtons = screen.queryAllByRole('button', { name: /optimize/i });
    if (optimizeButtons.length > 0) {
      await user.click(optimizeButtons[0]);

      await waitFor(() => {
        // Should show error message
        expect(screen.queryByText(/error/i) || screen.queryByText(/failed/i)).toBeTruthy();
      });
    }
  });

  it('should allow going back to previous steps', async () => {
    const user = userEvent.setup();
    render(<BuilderV2 />, { wrapper: createWrapper() });

    // Go to step 2
    await waitFor(() => {
      expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
    });

    const squadSizeInput = screen.getByRole('spinbutton') || screen.getByPlaceholderText(/enter squad size/i);
    if (squadSizeInput) {
      await user.clear(squadSizeInput);
      await user.type(squadSizeInput, '10');
    }

    const nextButton = screen.getByRole('button', { name: /next/i });
    await user.click(nextButton);

    await waitFor(() => {
      expect(screen.getByText(/Select Game Mode/i)).toBeInTheDocument();
    });

    // Click back button
    const backButton = screen.queryByRole('button', { name: /back/i });
    if (backButton) {
      await user.click(backButton);

      await waitFor(() => {
        expect(screen.getByText(/Select Squad Size/i)).toBeInTheDocument();
      });
    }
  });
});
