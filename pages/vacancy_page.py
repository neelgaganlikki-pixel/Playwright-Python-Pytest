"""Vacancy Page Object for OrangeHRM Recruitment > Vacancies."""

import re
from pathlib import Path

from playwright.sync_api import Page, expect


class VacancyPage:
    """Page Object for OrangeHRM Vacancy management."""

    __test__ = False

    def __init__(self, page: Page):
        self.page = page

        self.output_file = (
            Path(__file__).resolve().parent.parent
            / "tests"
            / "vacancy"
            / "vacancy_output.txt"
        )

        # ============================================================
        # RECRUITMENT NAVIGATION
        # ============================================================

        self.recruitment_nav_link = page.get_by_role(
            "link",
            name="Recruitment"
        )

        self.vacancies_link = page.get_by_role(
            "link",
            name="Vacancies"
        )

        # ============================================================
        # VACANCY LIST PAGE
        # ============================================================

        self.vacancies_header = page.get_by_role(
            "heading",
            name="Vacancies"
        )

        self.add_button = page.get_by_role(
            "button",
            name="Add"
        )

        # ============================================================
        # ADD VACANCY FORM
        # ============================================================

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

        self.save_button = page.get_by_role(
            "button",
            name="Save"
        )

    # ================================================================
    # LOGGED-IN USER
    # ================================================================

    def get_logged_in_user_name(self) -> str:
        """Return the logged-in username displayed in the header."""

        user_name = self.page.locator(
            ".oxd-userdropdown-name"
        )

        expect(
            user_name
        ).to_be_visible(timeout=10000)

        return user_name.inner_text().strip()

    # ================================================================
    # RECRUITMENT
    # ================================================================

    def click_recruitment(self) -> None:
        """Open Recruitment from the sidebar."""

        expect(
            self.recruitment_nav_link
        ).to_be_visible(timeout=10000)

        self.recruitment_nav_link.click()

        expect(
            self.page
        ).to_have_url(
            re.compile(
                r".*/web/index\.php/recruitment/.*"
            ),
            timeout=10000
        )

        print("Recruitment page opened.")

    # ================================================================
    # VACANCIES
    # ================================================================

    def click_vacancies(self) -> None:
        """Open the Vacancies page."""

        expect(
            self.vacancies_link
        ).to_be_visible(timeout=10000)

        self.vacancies_link.scroll_into_view_if_needed()

        self.vacancies_link.click()

        expect(
            self.page
        ).to_have_url(
            re.compile(
                r".*/web/index\.php/recruitment/viewJobVacancy.*"
            ),
            timeout=10000
        )

        expect(
            self.vacancies_header
        ).to_be_visible(timeout=10000)

        print("Vacancies page opened.")

    # ================================================================
    # ADD
    # ================================================================

    def click_add(self) -> None:
        """Click Add Vacancy."""

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

        print("Add Vacancy page opened.")

    # ================================================================
    # FILL VACANCY FORM
    # ================================================================

    def fill_vacancy_form(
        self,
        vacancy_data: dict
    ) -> None:
        """Fill the Add Vacancy form."""

        # ------------------------------------------------------------
        # Vacancy Name
        # ------------------------------------------------------------

        vacancy_name = vacancy_data.get("name")

        if not vacancy_name:
            raise ValueError(
                "Vacancy name is missing."
            )

        expect(
            self.vacancy_name_input
        ).to_be_visible(timeout=10000)

        self.vacancy_name_input.fill(
            vacancy_name
        )

        print(
            f"Vacancy name entered: {vacancy_name}"
        )

        # ------------------------------------------------------------
        # Job Title
        # ------------------------------------------------------------

        expect(
            self.job_title_dropdown
        ).to_be_visible(timeout=10000)

        self.job_title_dropdown.click()

        self.page.wait_for_selector(
            "div[role='listbox']",
            state="visible",
            timeout=10000
        )

        target_job_title = vacancy_data.get(
            "job_title"
        )

        job_option = None

        if target_job_title:

            candidate = self.page.get_by_role(
                "option",
                name=target_job_title,
                exact=True
            )

            if candidate.count() > 0:

                if candidate.first.is_visible():
                    job_option = candidate.first

        # ------------------------------------------------------------
        # Fallback to first available option
        # ------------------------------------------------------------

        if job_option is None:

            available_options = (
                self.page
                .locator(
                    "div[role='listbox'] "
                    "div[role='option']"
                )
            )

            if available_options.count() == 0:
                raise AssertionError(
                    "No Job Title options were available."
                )

            job_option = available_options.first

        expect(
            job_option
        ).to_be_visible(timeout=10000)

        job_option.click()

        print(
            "Job title selected."
        )

        # ------------------------------------------------------------
        # Description
        # ------------------------------------------------------------

        expect(
            self.description_textarea
        ).to_be_visible(timeout=10000)

        description = vacancy_data.get(
            "description",
            "Created by Playwright automation"
        )

        self.description_textarea.fill(
            description
        )

        print(
            "Description entered."
        )

        # ------------------------------------------------------------
        # Number of Positions
        # ------------------------------------------------------------

        expect(
            self.number_of_positions_input
        ).to_be_visible(timeout=10000)

        number_of_positions = vacancy_data.get(
            "number_of_positions",
            1
        )

        try:
            number_of_positions = int(
                number_of_positions
            )
        except (TypeError, ValueError):

            raise ValueError(
                "number_of_positions must be a valid integer."
            )

        if number_of_positions < 1:

            raise ValueError(
                "number_of_positions must be greater than 0."
            )

        self.number_of_positions_input.fill(
            str(number_of_positions)
        )

        print(
            "Number of positions entered: "
            f"{number_of_positions}"
        )

        # ------------------------------------------------------------
        # Hiring Manager
        # ------------------------------------------------------------

        expect(
            self.hiring_manager_input
        ).to_be_visible(timeout=10000)

        hiring_manager = vacancy_data.get(
            "hiring_manager"
        )

        if not hiring_manager:

            hiring_manager = (
                self.get_logged_in_user_name()
            )

        self.hiring_manager_input.fill(
            hiring_manager
        )

        print(
            f"Hiring manager entered: {hiring_manager}"
        )

        # ------------------------------------------------------------
        # Autocomplete
        # ------------------------------------------------------------

        autocomplete_dropdown = self.page.locator(
            ".oxd-autocomplete-dropdown"
        )

        try:

            expect(
                autocomplete_dropdown
            ).to_be_visible(timeout=10000)

        except AssertionError:

            raise AssertionError(
                "Hiring Manager autocomplete dropdown "
                "did not appear."
            )

        manager_option = (
            autocomplete_dropdown
            .locator(
                ".oxd-autocomplete-option"
            )
            .first
        )

        expect(
            manager_option
        ).to_be_visible(timeout=10000)

        manager_option.click()

        print(
            "Hiring manager selected."
        )

        print(
            "Vacancy form filled successfully."
        )

    # ================================================================
    # SAVE VACANCY
    # ================================================================

    def save_vacancy(self) -> None:
        """Save the vacancy and verify the success message."""

        expect(
            self.save_button
        ).to_be_visible(timeout=10000)

        expect(
            self.save_button
        ).to_be_enabled(timeout=10000)

        print(
            "Save button is visible and enabled."
        )

        print(
            "Clicking Save..."
        )

        self.save_button.click()

        print(
            "Save clicked."
        )

        # ------------------------------------------------------------
        # Check validation error
        # ------------------------------------------------------------

        invalid_positions = self.page.get_by_text(
            "Invalid Number of Positions",
            exact=True
        )

        if invalid_positions.is_visible(timeout=2000):

            raise AssertionError(
                "OrangeHRM rejected the vacancy because "
                "'Invalid Number of Positions' was displayed. "
                "Check number_of_positions in vacancy.json."
            )

        # ------------------------------------------------------------
        # Success Toast
        # ------------------------------------------------------------

        save_toast = self.page.get_by_text(
            "Successfully Saved",
            exact=True
        )

        expect(
            save_toast
        ).to_be_visible(timeout=10000)

        toast_text = (
            save_toast
            .inner_text()
            .strip()
        )

        print(
            "========================================"
        )

        print(
            f"TOAST MESSAGE: {toast_text}"
        )

        print(
            "========================================"
        )

        print(
            "Vacancy saved successfully."
        )

    # ================================================================
    # VERIFY VACANCY
    # ================================================================

    def verify_vacancy_in_list(
        self,
        vacancy_name: str
    ) -> None:
        """Verify the vacancy appears in the vacancy list."""

        current_url = self.page.url

        print(
            f"Current URL: {current_url}"
        )

        # ------------------------------------------------------------
        # Navigate to vacancy list if necessary
        # ------------------------------------------------------------

        if (
            "/recruitment/viewJobVacancy"
            not in current_url
        ):

            print(
                "Navigating to Vacancies list..."
            )

            expect(
                self.vacancies_link
            ).to_be_visible(timeout=10000)

            self.vacancies_link.scroll_into_view_if_needed()

            self.vacancies_link.click()

        # ------------------------------------------------------------
        # Verify URL
        # ------------------------------------------------------------

        expect(
            self.page
        ).to_have_url(
            re.compile(
                r".*/web/index\.php/recruitment/viewJobVacancy.*"
            ),
            timeout=10000
        )

        expect(
            self.vacancies_header
        ).to_be_visible(timeout=10000)

        # ------------------------------------------------------------
        # Find vacancy
        # ------------------------------------------------------------

        vacancy_row = (
            self.page
            .get_by_role(
                "row",
                name=re.compile(
                    re.escape(vacancy_name)
                )
            )
            .first
        )

        expect(
            vacancy_row
        ).to_be_visible(timeout=10000)

        print(
            f"Vacancy verified successfully: "
            f"{vacancy_name}"
        )

        self.save_vacancy_to_file(
            vacancy_name
        )

    # ================================================================
    # DELETE VACANCY
    # ================================================================

    def delete_vacancy(
        self,
        vacancy_name: str
    ) -> None:
        """Delete the vacancy and verify deletion."""

        # ------------------------------------------------------------
        # Navigate to vacancy list
        # ------------------------------------------------------------

        if (
            "/recruitment/viewJobVacancy"
            not in self.page.url
        ):

            expect(
                self.vacancies_link
            ).to_be_visible(timeout=10000)

            self.vacancies_link.scroll_into_view_if_needed()

            self.vacancies_link.click()

        # ------------------------------------------------------------
        # Verify list
        # ------------------------------------------------------------

        expect(
            self.page
        ).to_have_url(
            re.compile(
                r".*/web/index\.php/recruitment/viewJobVacancy.*"
            ),
            timeout=10000
        )

        expect(
            self.vacancies_header
        ).to_be_visible(timeout=10000)

        # ------------------------------------------------------------
        # Find vacancy row
        # ------------------------------------------------------------

        vacancy_row = (
            self.page
            .get_by_role(
                "row",
                name=re.compile(
                    re.escape(vacancy_name)
                )
            )
            .first
        )

        expect(
            vacancy_row
        ).to_be_visible(timeout=10000)

        vacancy_row.scroll_into_view_if_needed()

        print(
            f"Vacancy found for deletion: "
            f"{vacancy_name}"
        )

        # ------------------------------------------------------------
        # Find action button
        # ------------------------------------------------------------

        action_button = (
            vacancy_row
            .get_by_role("button")
            .first
        )

        expect(
            action_button
        ).to_be_visible(timeout=5000)

        expect(
            action_button
        ).to_be_enabled(timeout=5000)

        action_button.click()

        print(
            "Vacancy action menu opened."
        )

        # ------------------------------------------------------------
        # Delete option
        # ------------------------------------------------------------

        delete_option = self.page.get_by_text(
            " Yes, Delete ",
            exact=True
        ).last

        expect(
            delete_option
        ).to_be_visible(timeout=5000)

        delete_option.click()

        print(
            "Delete confirmation clicked."
        )

        # ------------------------------------------------------------
        # Delete toast
        # ------------------------------------------------------------

        delete_toast = self.page.get_by_text(
            "Successfully Deleted",
            exact=True
        )

        expect(
            delete_toast
        ).to_be_visible(timeout=10000)

        print(
            "Vacancy deleted successfully."
        )

        # ------------------------------------------------------------
        # Verify row is gone
        # ------------------------------------------------------------

        expect(
            self.page.get_by_role(
                "row",
                name=re.compile(
                    re.escape(vacancy_name)
                )
            )
        ).to_have_count(0)

        print(
            f"Vacancy row removed: "
            f"{vacancy_name}"
        )

    # ================================================================
    # SAVE VACANCY NAME
    # ================================================================

    def save_vacancy_to_file(
        self,
        vacancy_name: str
    ) -> None:
        """Save vacancy name to output file."""

        self.output_file.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        self.output_file.write_text(
            vacancy_name,
            encoding="utf-8"
        )

        print(
            f"Vacancy name saved to: "
            f"{self.output_file}"
        )

    # ================================================================
    # COMPLETE CREATE FLOW
    # ================================================================

    def create_vacancy(
        self,
        vacancy_data: dict
    ) -> str:
        """Create and verify a vacancy."""

        # ------------------------------------------------------------
        # Recruitment
        # ------------------------------------------------------------

        self.click_recruitment()

        # ------------------------------------------------------------
        # Vacancies
        # ------------------------------------------------------------

        self.click_vacancies()

        # ------------------------------------------------------------
        # Add
        # ------------------------------------------------------------

        self.click_add()

        # ------------------------------------------------------------
        # Hiring Manager
        # ------------------------------------------------------------

        if not vacancy_data.get(
            "hiring_manager"
        ):

            vacancy_data["hiring_manager"] = (
                self.get_logged_in_user_name()
            )

        print(
            "Current logged-in user: "
            f"{vacancy_data['hiring_manager']}"
        )

        # ------------------------------------------------------------
        # Fill form
        # ------------------------------------------------------------

        self.fill_vacancy_form(
            vacancy_data
        )

        # ------------------------------------------------------------
        # Save
        # ------------------------------------------------------------

        self.save_vacancy()

        # ------------------------------------------------------------
        # Verify
        # ------------------------------------------------------------

        self.verify_vacancy_in_list(
            vacancy_data["name"]
        )

        return vacancy_data["name"]
