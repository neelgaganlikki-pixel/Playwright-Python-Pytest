```python
"""Vacancy Page Object for OrangeHRM Vacancy module."""

import re
from pathlib import Path

from playwright.sync_api import Page, expect

from config.config_reader import config


class VacancyPage:
    """Page Object for OrangeHRM Recruitment > Vacancies."""

    __test__ = False

    def __init__(self, page: Page):
        self.page = page

        self.output_file = (
            Path(__file__).resolve().parent.parent
            / "tests"
            / "vacancy"
            / "vacancy_output.txt"
        )

        # --------------------------------------------------------------
        # Sidebar navigation
        # --------------------------------------------------------------
        self.recruitment_nav_link = page.get_by_role(
            "link",
            name="Recruitment"
        )

        # --------------------------------------------------------------
        # Top-bar menu on Recruitment page
        # --------------------------------------------------------------
        self.vacancies_link = page.get_by_role(
            "link",
            name="Vacancies"
        )

        # --------------------------------------------------------------
        # Vacancy list page
        # --------------------------------------------------------------
        self.vacancies_header = page.get_by_role(
            "heading",
            name="Vacancies"
        )

        self.add_button = page.get_by_role(
            "button",
            name="Add"
        )

        # --------------------------------------------------------------
        # Add Vacancy form
        # --------------------------------------------------------------

        self.vacancy_name_input = (
            page.locator("div.oxd-input-group")
            .filter(has_text="Vacancy Name")
            .locator("input")
            .first
        )

        self.job_title_dropdown = page.locator(
            ".oxd-select-text"
        ).first

        self.description_textarea = page.get_by_placeholder(
            "Type description here"
        )

        self.hiring_manager_input = page.get_by_placeholder(
            "Type for hints..."
        )

        self.number_of_positions_input = (
            page.locator("div.oxd-input-group")
            .filter(has_text="Number of Positions")
            .locator("input")
            .first
        )

        self.active_checkbox = page.locator(
            "input[type='checkbox']"
        ).first

        self.publish_checkbox = page.locator(
            "input[type='checkbox']"
        ).nth(1)

        self.save_button = page.get_by_role(
            "button",
            name="Save"
        )

        # --------------------------------------------------------------
        # Toast
        # --------------------------------------------------------------

        self.toast_message = page.locator(
            ".oxd-toast-container.oxd-toast-container--bottom:visible"
        )

        # --------------------------------------------------------------
        # Vacancy action menu
        # --------------------------------------------------------------

        self.delete_menu_item = page.locator(
            ".oxd-icon.bi-trash"
        ).get_by_text(
            "Delete",
            exact=True
        )

    # ==================================================================
    # Helper
    # ==================================================================

    def get_logged_in_user_name(self) -> str:
        """Return the profile name shown in the top-right corner."""

        user_name = self.page.locator(
            ".oxd-userdropdown-name"
        )

        expect(user_name).to_be_visible(timeout=10000)

        return user_name.inner_text().strip()

    # ==================================================================
    # Step 2 – Click Recruitment
    # ==================================================================

    def click_recruitment(self) -> None:
        """Click the Recruitment link in the sidebar."""

        expect(
            self.recruitment_nav_link
        ).to_be_visible(timeout=10000)

        self.recruitment_nav_link.click()

        expect(self.page).to_have_url(
            re.compile(
                r".*/web/index\.php/recruitment/.*"
            ),
            timeout=10000
        )

    # ==================================================================
    # Step 3 – Click Vacancies
    # ==================================================================

    def click_vacancies(self) -> None:
        """Click the Vacancies link in the top-bar menu."""

        expect(
            self.vacancies_link
        ).to_be_visible(timeout=10000)

        self.vacancies_link.scroll_into_view_if_needed()

        self.vacancies_link.click()

        expect(self.page).to_have_url(
            re.compile(
                r".*/web/index\.php/recruitment/viewJobVacancy.*"
            ),
            timeout=10000
        )

        expect(
            self.vacancies_header
        ).to_be_visible(timeout=10000)

        print("Vacancies list loaded.")

    # ==================================================================
    # Step 4 – Add Vacancy
    # ==================================================================

    def click_add(self) -> None:
        """Click the Add button on the Vacancies list page."""

        expect(
            self.add_button
        ).to_be_visible(timeout=10000)

        expect(
            self.add_button
        ).to_be_enabled(timeout=10000)

        self.add_button.click()

        expect(
            self.vacancy_name_input
        ).to_be_visible(timeout=10000)

        print("Add Vacancy page loaded.")

    # ==================================================================
    # Step 5 – Fill Vacancy Details
    # ==================================================================

    def fill_vacancy_form(
        self,
        vacancy_data: dict
    ) -> None:
        """Fill every field on the Add Vacancy form."""

        # --------------------------------------------------------------
        # Vacancy Name
        # --------------------------------------------------------------

        if "name" in vacancy_data:

            expect(
                self.vacancy_name_input
            ).to_be_visible(timeout=10000)

            self.vacancy_name_input.fill(
                vacancy_data["name"]
            )

            print(
                f"Vacancy name entered: "
                f"{vacancy_data['name']}"
            )

        # --------------------------------------------------------------
        # Job Title
        # --------------------------------------------------------------

        expect(
            self.job_title_dropdown
        ).to_be_visible(timeout=10000)

        self.job_title_dropdown.click()

        self.page.wait_for_selector(
            "div[role='listbox']",
            state="visible",
            timeout=10000
        )

        target_title = vacancy_data.get(
            "job_title"
        )

        job_option = None

        if target_title:

            candidate_option = self.page.get_by_role(
                "option",
                name=target_title
            )

            if (
                candidate_option.count() > 0
                and candidate_option.first.is_visible()
            ):
                job_option = candidate_option.first

        # --------------------------------------------------------------
        # Fallback to first valid job title
        # --------------------------------------------------------------

        if job_option is None:

            job_option = (
                self.page.locator(
                    "div[role='listbox'] "
                    "div[role='option']"
                )
                .filter(
                    has_not_text="-- Select --"
                )
                .filter(
                    has_not_text="No Records Found"
                )
                .first
            )

        expect(
            job_option
        ).to_be_visible(timeout=5000)

        job_option.click()

        # --------------------------------------------------------------
        # Description
        # --------------------------------------------------------------

        expect(
            self.description_textarea
        ).to_be_visible(timeout=10000)

        self.description_textarea.fill(
            vacancy_data.get(
                "description",
                "Created by Playwright automation"
            )
        )

        # --------------------------------------------------------------
        # Number of Positions
        # --------------------------------------------------------------

        expect(
            self.number_of_positions_input
        ).to_be_visible(timeout=10000)

        number_of_positions = int(
            vacancy_data.get(
                "number_of_positions",
                1
            )
        )

        if number_of_positions < 1:

            raise ValueError(
                "Invalid number_of_positions: "
                f"{number_of_positions}. "
                "Value must be greater than 0."
            )

        self.number_of_positions_input.fill(
            str(number_of_positions)
        )

        print(
            "Number of positions entered: "
            f"{number_of_positions}"
        )

        # --------------------------------------------------------------
        # Hiring Manager
        # --------------------------------------------------------------

        expect(
            self.hiring_manager_input
        ).to_be_visible(timeout=10000)

        self.hiring_manager_input.fill(
            vacancy_data["hiring_manager"]
        )

        # --------------------------------------------------------------
        # Wait for autocomplete dropdown
        # --------------------------------------------------------------

        autocomplete_dropdown = self.page.locator(
            ".oxd-autocomplete-dropdown"
        )

        expect(
            autocomplete_dropdown
        ).to_be_visible(timeout=60000)

        manager_option = (
            autocomplete_dropdown
            .locator(
                ".oxd-autocomplete-option"
            )
            .first
        )

        expect(
            manager_option
        ).to_be_visible(timeout=60000)

        self.page.wait_for_timeout(1000)

        manager_option.click()

        print("Hiring manager selected.")

        print("Vacancy form filled successfully.")

    # ==================================================================
    # Step 6 – Save Vacancy
    # ==================================================================

    def save_vacancy(self) -> None:
        """
        Save vacancy and verify successful creation.

        Does not assume a specific URL after Save.
        """

        expect(
            self.save_button
        ).to_be_visible(timeout=10000)

        expect(
            self.save_button
        ).to_be_enabled(timeout=10000)

        print(
            "Save button is visible and enabled."
        )

        print("Clicking Save...")

        self.save_button.click()

        print("Save clicked.")

        # --------------------------------------------------------------
        # Check for validation error
        # --------------------------------------------------------------

        invalid_positions = self.page.get_by_text(
            "Invalid Number of Positions",
            exact=True
        )

        try:

            expect(
                invalid_positions
            ).to_be_visible(timeout=20
```
