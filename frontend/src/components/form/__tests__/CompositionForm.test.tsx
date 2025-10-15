import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { vi } from "vitest";
import { CompositionForm } from "../CompositionForm";
// CompositionFormSchema n'est pas utilisé directement dans les tests

// Mock des dépendances externes
vi.mock("@/components/form/ProfessionSelect", () => ({
  ProfessionSelect: vi.fn(
    ({
      value = [],
      onChange,
    }: {
      value: string[];
      onChange: (value: string[]) => void;
    }) => (
      <div data-testid="profession-select">
        <button
          onClick={() => onChange([...value, "Guardian"])}
          data-testid="add-profession"
        >
          Add Profession
        </button>
        <div data-testid="selected-professions">
          {value.map((prof: string) => (
            <div key={prof} data-testid={`selected-${prof}`}>
              {prof}
            </div>
          ))}
        </div>
      </div>
    ),
  ),
}));

describe("CompositionForm", () => {
  const mockOnSubmit = jest.fn();
  const defaultProps = {
    onSubmit: mockOnSubmit,
    submitLabel: "Enregistrer",
  };

  beforeEach(() => {
    mockOnSubmit.mockClear();
  });

  const fillAndSubmitForm = async (data: {
    name: string;
    description?: string;
    squad_size?: number;
  }) => {
    await userEvent.type(
      screen.getByLabelText(/nom de la composition/i),
      data.name,
    );

    if (data.description) {
      await userEvent.type(
        screen.getByLabelText(/description/i),
        data.description,
      );
    }

    if (data.squad_size) {
      const sizeInput = screen.getByLabelText(/taille de l'escouade/i);
      await userEvent.clear(sizeInput);
      await userEvent.type(sizeInput, data.squad_size.toString());
    }

    // Ajouter une profession
    await userEvent.click(screen.getByTestId("add-profession"));

    // Soumettre le formulaire
    await userEvent.click(screen.getByRole("button", { name: /enregistrer/i }));
  };

  it("renders the form with all fields", () => {
    render(<CompositionForm {...defaultProps} />);

    expect(screen.getByLabelText(/nom de la composition/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/description/i)).toBeInTheDocument();
    expect(screen.getByLabelText(/taille de l'escouade/i)).toBeInTheDocument();
    expect(screen.getByText(/professions/i)).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: /enregistrer/i }),
    ).toBeInTheDocument();
  });

  it("validates required fields", async () => {
    render(<CompositionForm {...defaultProps} />);

    // Soumettre sans remplir les champs requis
    await userEvent.click(screen.getByRole("button", { name: /enregistrer/i }));

    // Vérifier les messages d'erreur
    expect(await screen.findByText(/le nom est requis/i)).toBeInTheDocument();
    expect(mockOnSubmit).not.toHaveBeenCalled();
  });

  it("submits the form with valid data", async () => {
    render(<CompositionForm {...defaultProps} />);

    const formData = {
      name: "Test Composition",
      description: "This is a test composition",
      squad_size: 10,
    };

    await fillAndSubmitForm(formData);

    // Vérifier que la fonction de soumission a été appelée avec les bonnes données
    await waitFor(() => {
      expect(mockOnSubmit).toHaveBeenCalledWith(
        expect.objectContaining({
          name: formData.name,
          description: formData.description,
          squad_size: formData.squad_size,
          professions: ["Guardian"],
        }),
      );
    });
  });

  it("displays default values when provided", () => {
    const defaultValues = {
      name: "Default Composition",
      description: "Default description",
      squad_size: 15,
      professions: ["Warrior", "Guardian"],
    };

    render(<CompositionForm {...defaultProps} defaultValues={defaultValues} />);

    expect(screen.getByDisplayValue(defaultValues.name)).toBeInTheDocument();
    expect(
      screen.getByDisplayValue(defaultValues.description),
    ).toBeInTheDocument();
    expect(
      screen.getByDisplayValue(defaultValues.squad_size),
    ).toBeInTheDocument();

    // Vérifier que les professions par défaut sont affichées
    defaultValues.professions.forEach((prof) => {
      expect(screen.getByText(prof)).toBeInTheDocument();
    });
  });

  it("displays loading state when submitting", async () => {
    // Utilisation d'un mock plus simple pour le test de chargement
    const mockSubmit = jest.fn().mockResolvedValue(undefined);

    render(
      <CompositionForm
        {...defaultProps}
        onSubmit={mockSubmit}
        isSubmitting={true} // Forcer l'état de chargement
      />,
    );

    // Vérifier que le bouton est désactivé pendant le chargement
    const submitButton = screen.getByRole("button", { name: /enregistrer/i });
    expect(submitButton).toBeDisabled();
  });

  it("displays custom submit button label", () => {
    const customLabel = "Custom Submit";
    render(<CompositionForm {...defaultProps} submitLabel={customLabel} />);

    expect(
      screen.getByRole("button", { name: customLabel }),
    ).toBeInTheDocument();
  });
});
