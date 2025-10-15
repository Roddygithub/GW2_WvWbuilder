import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { ProfessionSelect } from "../ProfessionSelect";
import { PROFESSIONS_DATA } from "@/data/professions";

describe("ProfessionSelect", () => {
  const mockOnChange = jest.fn();
  const defaultProps = {
    value: [],
    onChange: mockOnChange,
    maxSelections: 5,
  };

  beforeEach(() => {
    mockOnChange.mockClear();
  });

  it("renders the select button with placeholder", () => {
    render(<ProfessionSelect {...defaultProps} />);
    // Find the button by its role and content
    const button = screen.getByRole("button");
    expect(button).toHaveTextContent(/sélectionner des professions/i);
  });

  it("shows the number of selected professions", () => {
    const selected = ["Guardian", "Warrior"];
    render(<ProfessionSelect {...defaultProps} value={selected} />);
    expect(
      screen.getByText(`${selected.length} profession(s) sélectionnée(s)`),
    ).toBeInTheDocument();
  });

  it("opens the popover when clicking the button", async () => {
    render(<ProfessionSelect {...defaultProps} />);
    const button = screen.getByRole("button");
    await userEvent.click(button);

    expect(
      screen.getByPlaceholderText(/rechercher une profession/i),
    ).toBeInTheDocument();
    Object.keys(PROFESSIONS_DATA).forEach((profession) => {
      expect(screen.getByText(profession)).toBeInTheDocument();
    });
  });

  it("allows selecting and deselecting professions", async () => {
    render(<ProfessionSelect {...defaultProps} />);
    const button = screen.getByRole("button");
    await userEvent.click(button);

    // Select a profession
    const guardianOption = screen.getByRole("option", { name: /guardian/i });
    await userEvent.click(guardianOption);

    expect(mockOnChange).toHaveBeenCalledWith(["Guardian"]);

    // Deselect the profession
    mockOnChange.mockClear();
    await userEvent.click(guardianOption);
    expect(mockOnChange).toHaveBeenCalledWith([]);
  });

  it("filters professions based on search input", async () => {
    render(<ProfessionSelect {...defaultProps} />);
    await userEvent.click(screen.getByRole("button"));

    const searchInput = screen.getByPlaceholderText(
      /rechercher une profession/i,
    );
    await userEvent.type(searchInput, "guard");

    expect(screen.getByText("Guardian")).toBeInTheDocument();
    expect(screen.queryByText("Warrior")).not.toBeInTheDocument();
  });

  it("respects the maxSelections prop", async () => {
    const maxSelections = 2;
    render(
      <ProfessionSelect
        {...defaultProps}
        value={["Guardian", "Warrior"]}
        maxSelections={maxSelections}
      />,
    );

    await userEvent.click(screen.getByRole("button"));

    // Try to select a third profession
    const elementalistOption = screen.getByRole("option", {
      name: /elementalist/i,
    });
    await userEvent.click(elementalistOption);

    // Should not call onChange as maxSelections is reached
    expect(mockOnChange).not.toHaveBeenCalled();
  });

  it("allows removing selected professions using the remove button", async () => {
    const selected = ["Guardian", "Warrior"];
    render(<ProfessionSelect {...defaultProps} value={selected} />);

    // Find the remove button for Guardian using test id
    const removeButton = screen.getByTestId("remove-profession-Guardian");
    await userEvent.click(removeButton);
    expect(mockOnChange).toHaveBeenCalledWith(["Warrior"]);
  });
});
