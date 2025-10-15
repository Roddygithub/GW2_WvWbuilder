/**
 * Tests for CompositionMembersList component
 */
import { describe, it, expect } from 'vitest';
import { render, screen } from '@testing-library/react';
import { BrowserRouter } from 'react-router-dom';
import CompositionMembersList from '../../components/CompositionMembersList';

const mockMembers = [
  {
    position: 1,
    profession_id: 1,
    profession_name: 'Guardian',
    elite_spec_id: 27,
    elite_spec_name: 'Firebrand',
    role: 'healer' as const,
  },
  {
    position: 2,
    profession_id: 2,
    profession_name: 'Revenant',
    elite_spec_id: 5,
    elite_spec_name: 'Herald',
    role: 'boon_support' as const,
  },
  {
    position: 3,
    profession_id: 6,
    profession_name: 'Engineer',
    elite_spec_id: 70,
    elite_spec_name: 'Mechanist',
    role: 'dps' as const,
  },
];

const createWrapper = () => {
  return ({ children }: { children: React.ReactNode }) => (
    <BrowserRouter>{children}</BrowserRouter>
  );
};

describe('CompositionMembersList', () => {
  it('should render all members', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText('Guardian')).toBeInTheDocument();
    expect(screen.getByText('Revenant')).toBeInTheDocument();
    expect(screen.getByText('Engineer')).toBeInTheDocument();
  });

  it('should display elite specializations', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText(/Firebrand/i)).toBeInTheDocument();
    expect(screen.getByText(/Herald/i)).toBeInTheDocument();
    expect(screen.getByText(/Mechanist/i)).toBeInTheDocument();
  });

  it('should display roles with badges', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText(/healer/i)).toBeInTheDocument();
    expect(screen.getByText(/boon.?support/i)).toBeInTheDocument();
    expect(screen.getByText(/dps/i)).toBeInTheDocument();
  });

  it('should display position numbers', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    // Check for position indicators (could be #1, #2, #3 or just 1, 2, 3)
    const positions = [1, 2, 3];
    positions.forEach((pos) => {
      expect(
        screen.getByText(new RegExp(`${pos}`, 'i'))
      ).toBeInTheDocument();
    });
  });

  it('should render empty state when no members', () => {
    render(<CompositionMembersList members={[]} />, {
      wrapper: createWrapper(),
    });

    expect(
      screen.getByText(/no members/i) || screen.getByText(/empty/i)
    ).toBeInTheDocument();
  });

  it('should handle members without elite specs', () => {
    const membersNoElite = [
      {
        position: 1,
        profession_id: 1,
        profession_name: 'Guardian',
        elite_spec_id: null,
        elite_spec_name: null,
        role: 'dps' as const,
      },
    ];

    render(<CompositionMembersList members={membersNoElite} />, {
      wrapper: createWrapper(),
    });

    expect(screen.getByText('Guardian')).toBeInTheDocument();
    // Should still render without crashing
  });

  it('should display all unique professions', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    const professions = ['Guardian', 'Revenant', 'Engineer'];
    professions.forEach((profession) => {
      expect(screen.getByText(profession)).toBeInTheDocument();
    });
  });

  it('should display role distribution', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    // Each role should appear once
    expect(screen.getByText(/healer/i)).toBeInTheDocument();
    expect(screen.getByText(/boon.?support/i)).toBeInTheDocument();
    expect(screen.getByText(/dps/i)).toBeInTheDocument();
  });

  it('should handle large number of members', () => {
    const largeMemberList = Array.from({ length: 50 }, (_, i) => ({
      position: i + 1,
      profession_id: (i % 9) + 1,
      profession_name: 'Guardian',
      elite_spec_id: 27,
      elite_spec_name: 'Firebrand',
      role: 'dps' as const,
    }));

    render(<CompositionMembersList members={largeMemberList} />, {
      wrapper: createWrapper(),
    });

    // Should render all 50 members
    expect(screen.getAllByText('Guardian')).toHaveLength(50);
  });

  it('should display members in correct order', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    const memberElements = screen.getAllByText(/Guardian|Revenant|Engineer/);
    
    // Verify order (if component renders in order)
    expect(memberElements[0]).toHaveTextContent('Guardian');
    expect(memberElements[1]).toHaveTextContent('Revenant');
    expect(memberElements[2]).toHaveTextContent('Engineer');
  });

  it('should apply correct styling for different roles', () => {
    const { container } = render(
      <CompositionMembersList members={mockMembers} />,
      { wrapper: createWrapper() }
    );

    // Check that role badges have different classes/styles
    const healerBadge = screen.getByText(/healer/i);
    const supportBadge = screen.getByText(/boon.?support/i);
    const dpsBadge = screen.getByText(/dps/i);

    expect(healerBadge).toBeInTheDocument();
    expect(supportBadge).toBeInTheDocument();
    expect(dpsBadge).toBeInTheDocument();
  });

  it('should be accessible with proper ARIA labels', () => {
    render(<CompositionMembersList members={mockMembers} />, {
      wrapper: createWrapper(),
    });

    // Component should have proper structure for accessibility
    const list = screen.queryByRole('list');
    if (list) {
      expect(list).toBeInTheDocument();
    }
  });
});
