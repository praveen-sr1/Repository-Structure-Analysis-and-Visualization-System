import { render, screen } from "@testing-library/react";
import userEvent from "@testing-library/user-event";
import { beforeEach, describe, expect, it } from "vitest";

import { SearchBar } from "@/components/common/SearchBar";
import { useUiStore } from "@/stores/uiStore";

describe("SearchBar", () => {
  beforeEach(() => {
    useUiStore.setState({ searchQuery: "" });
  });

  it("updates the search query in the store as the user types", async () => {
    const user = userEvent.setup();
    render(<SearchBar />);

    const input = screen.getByPlaceholderText("Search files…");
    await user.type(input, "utils");

    expect(useUiStore.getState().searchQuery).toBe("utils");
  });

  it("clears the query when the clear button is clicked", async () => {
    const user = userEvent.setup();
    useUiStore.setState({ searchQuery: "main" });
    render(<SearchBar />);

    await user.click(screen.getByLabelText("Clear search"));
    expect(useUiStore.getState().searchQuery).toBe("");
  });
});
