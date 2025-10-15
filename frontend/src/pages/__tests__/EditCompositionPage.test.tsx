import { render, screen, waitFor } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { MemoryRouter, Route, Routes } from "react-router-dom";
import { vi } from "vitest";
import EditCompositionPage from "../EditCompositionPage";

// Mock des dépendances
const mockToast = vi.fn();

// Créer les mocks avant de les utiliser dans les mocks de modules
const mockNavigate = vi.fn();
const mockUseParams = vi.fn();

// Mock use-toast
vi.mock("@/components/ui/use-toast", () => ({
  useToast: () => ({ toast: mockToast }),
}));

// Mock react-router-dom
vi.mock("react-router-dom", async () => {
  const actual = await vi.importActual("react-router-dom");
  return {
    ...actual,
    useParams: () => mockUseParams(),
    useNavigate: () => mockNavigate,
  };
});

// Mock des appels API
const mockFetch = vi.fn();
global.fetch = mockFetch;

// Configuration du test
const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      retry: false,
    },
  },
});

const wrapper = ({ children }: { children: React.ReactNode }) => (
  <QueryClientProvider client={queryClient}>
    <MemoryRouter>
      <Routes>
        <Route path="/" element={children} />
        <Route path="/compositions" element={<div>Compositions List</div>} />
        <Route
          path="/compositions/:id"
          element={<div>Composition Detail</div>}
        />
      </Routes>
    </MemoryRouter>
  </QueryClientProvider>
);

describe("EditCompositionPage", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    queryClient.clear();
    mockFetch.mockReset();
  });

  it("renders loading state when fetching composition", () => {
    render(<EditCompositionPage />, { wrapper });
    expect(screen.getByRole("status")).toBeInTheDocument();
  });

  it("handles create mode correctly", async () => {
    // Simuler une réponse API réussie
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: "new-id",
        name: "New Composition",
        description: "Test Description",
        squad_size: 10,
        professions: [],
        playstyle: "balanced",
      }),
    });

    render(<EditCompositionPage />, { wrapper });

    // Remplir le formulaire
    await userEvent.type(
      await screen.findByLabelText(/nom de la composition/i),
      "New Composition",
    );

    // Soumettre le formulaire
    await userEvent.click(
      screen.getByRole("button", { name: /créer la composition/i }),
    );

    // Vérifier que la requête a été envoyée
    expect(mockFetch).toHaveBeenCalled();

    // Vérifier que la navigation a eu lieu
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/compositions");
    });

    // Vérifier que le toast de succès est affiché
    expect(mockToast).toHaveBeenCalledWith({
      title: "Succès",
      description: expect.stringContaining(
        "La composition a été créée avec succès",
      ),
    });
  });

  it("handles edit mode correctly", async () => {
    // Simuler un paramètre d'URL avec un ID
    mockUseParams.mockReturnValue({ id: "1" });

    // Reset mock before setting up the new response
    mockFetch.mockReset();
    // Simuler la réponse de l'API pour le chargement
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: "1",
        name: "Existing Composition",
        description: "Existing Description",
        squad_size: 15,
        profs: ["Guardian", "Warrior"],
        playstyle: "offensive",
      }),
    });

    // Reset mock before setting up the update response
    mockFetch.mockReset();
    // Simuler la réponse pour la mise à jour
    mockFetch.mockResolvedValueOnce({
      ok: true,
      json: async () => ({
        id: "1",
        name: "Updated Composition",
        description: "Updated Description",
        squad_size: 15,
        profs: ["Guardian", "Warrior"],
        playstyle: "offensive",
      }),
    });

    render(<EditCompositionPage />, { wrapper });

    // Attendre que le formulaire soit chargé
    await screen.findByDisplayValue("Existing Composition");

    // Modifier un champ
    const nameInput = screen.getByLabelText(/nom de la composition/i);
    await userEvent.clear(nameInput);
    await userEvent.type(nameInput, "Updated Composition");

    // Soumettre le formulaire
    await userEvent.click(
      screen.getByRole("button", { name: /mettre à jour/i }),
    );

    // Vérifier que la requête a été envoyée
    expect(mockFetch).toHaveBeenCalled();

    // Vérifier que la navigation a eu lieu
    await waitFor(() => {
      expect(mockNavigate).toHaveBeenCalledWith("/compositions/1");
    });

    // Vérifier que le toast de succès est affiché
    expect(mockToast).toHaveBeenCalledWith({
      title: "Succès",
      description: expect.stringContaining(
        "La composition a été mise à jour avec succès",
      ),
    });
  });

  it("handles API errors", async () => {
    // Simuler une erreur d'API
    mockFetch.mockResolvedValueOnce({
      ok: false,
      status: 500,
      json: async () => ({
        message: "Internal Server Error",
      }),
    });

    render(<EditCompositionPage />, { wrapper });

    // Remplir et soumettre le formulaire
    await userEvent.type(
      await screen.findByLabelText(/nom de la composition/i),
      "Error Test",
    );

    await userEvent.click(
      screen.getByRole("button", { name: /créer la composition/i }),
    );

    // Vérifier que le toast d'erreur est affiché
    await waitFor(() => {
      expect(mockToast).toHaveBeenCalledWith({
        title: "Erreur",
        description: expect.stringContaining("Une erreur est survenue"),
        variant: "destructive",
      });
    });
  });
});
