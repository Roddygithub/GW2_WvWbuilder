/**
 * GW2Optimizer - SquadCard Tests
 * Tests unitaires pour le composant SquadCard
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { SquadCard } from '@/components/squad/SquadCard';
import { Squad } from '@/types/gw2optimizer';

const mockSquad: Squad = {
  id: 'squad-1',
  name: 'Test Squad',
  builds: [
    {
      id: '1',
      profession: 'Guardian',
      specialization: 'Firebrand',
      role: 'Support',
      count: 3,
      weight: 0.85,
    },
    {
      id: '2',
      profession: 'Engineer',
      specialization: 'Scrapper',
      role: 'Support',
      count: 2,
      weight: 1.1,
    },
  ],
  weight: 0.95,
  synergy: 0.87,
  buffs: ['Quickness +95%', 'Stability +90%'],
  nerfs: [],
  timestamp: '2025-10-18T12:00:00',
  mode: 'zerg',
  squad_size: 15,
};

describe('SquadCard', () => {
  it('renders squad name correctly', () => {
    render(<SquadCard squad={mockSquad} />);
    expect(screen.getByText('Test Squad')).toBeInTheDocument();
  });

  it('displays weight and synergy stats', () => {
    render(<SquadCard squad={mockSquad} />);
    expect(screen.getByText('95%')).toBeInTheDocument();
    expect(screen.getByText('87%')).toBeInTheDocument();
  });

  it('shows all builds', () => {
    render(<SquadCard squad={mockSquad} />);
    expect(screen.getByText('Firebrand')).toBeInTheDocument();
    expect(screen.getByText('Scrapper')).toBeInTheDocument();
  });

  it('displays buffs correctly', () => {
    render(<SquadCard squad={mockSquad} />);
    expect(screen.getByText('Quickness +95%')).toBeInTheDocument();
    expect(screen.getByText('Stability +90%')).toBeInTheDocument();
  });

  it('calls onSelect when clicked', () => {
    const handleSelect = vi.fn();
    render(<SquadCard squad={mockSquad} onSelect={handleSelect} />);
    
    const card = screen.getByText('Test Squad').closest('div');
    if (card) {
      fireEvent.click(card);
      expect(handleSelect).toHaveBeenCalledWith('squad-1');
    }
  });

  it('expands to show details when Details button clicked', () => {
    render(<SquadCard squad={mockSquad} />);
    
    const detailsButton = screen.getByText('Details');
    fireEvent.click(detailsButton);
    
    expect(screen.getByText('Detailed Analysis')).toBeInTheDocument();
  });

  it('shows mode badge', () => {
    render(<SquadCard squad={mockSquad} />);
    expect(screen.getByText('Mode: ZERG')).toBeInTheDocument();
  });
});
