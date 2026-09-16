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
        self.output_file = Path(__file__).resolve().parent.parent / "tests" / "vacancy" / "vacancy_output.txt"

        # --- Sidebar navigation ---
        self.recruitment_nav_link = page.get_by_role("link", name="Recruitment")

        # --- Top-bar menu on Recruitment page ---
        self.vacancies_link = page.get_by_role("link", name="Vacancies")

        # --- Vacancy list page ---
        self.vacancies_header = page.get_by_role("heading", name="Vacancies")
        self.add_button = page.get_by_role("button", name="Add")

        # --- Add Vacancy form elements ---
        self.vacancy_name_input = page.locator("div.oxd-input-group").filter(has_text="Vacancy Name").locator("input").first
        self.job_title_dropdown = page.locator(".oxd-select-text").first
        self.description_textarea = page.get_by_placeholder("Type description here")
        self.hiring_manager_input = page.get_by_placeholder("Type for hints...")
        self.number_of_positions_input = page.locator("div.oxd-input-group").filter(has_text="Number of Positions").locator("input").first
        self.active_checkbox = page.locator("input[type='checkbox']").first
        self.publish_checkbox = page.locator("input[type='checkbox']").nth(1)
        self.save_button = page.get_by_role("button", name="Save")

        # --- Toast ---
        self.toast_message = page.locator(".oxd-toast-container.oxd-toast-container--bottom:visible")
        
        # --- Vacancy action menu ---
        self.delete_menu_item = page.locator(".oxd-icon bi-trash").get_by_text("Delete", exact=True)

    # ------------------------------------------------------------------
    # Helper
    # ------------------------------------------------------------------

    def get_logged_in_user_name(self) -> str:
        """Return the profile name shown in the top-right corner."""
        user_name = self.page.locator(".oxd-userdropdown-name")
        expect(user_name).to_be_visible()
        return user_name.inner_text().strip()

    # ------------------------------------------------------------------
    # Step 2 – Click on Recruitment
    # ------------------------------------------------------------------

    def click_recruitment(self) -> None:
        """Click the Recruitment link in the sidebar."""
        expect(self.recruitment_nav_link).to_be_visible()
        self.recruitment_nav_link.click()
        expect(self.page).to_have_url(re.compile(r".*/web/index\.php/recruitment/.*"))

    # ------------------------------------------------------------------
    # Step 3 – Click on Vacancies
    # ------------------------------------------------------------------

    def click_vacancies(self) -> None:
        """Click the Vacancies link in the top-bar menu."""
        expect(self.vacancies_link).to_be_visible()
        self.vacancies_link.scroll_into_view_if_needed()
        self.vacancies_link.click()
        expect(self.page).to_have_url(re.compile(r".*/web/index\.php/recruitment/viewJobVacancy.*"), timeout=10000)
        expect(self.vacancies_header).to_be_visible(timeout=10000)

    # ------------------------------------------------------------------
    # Step 4 – Add new vacancy
    # ------------------------------------------------------------------

    def click_add(self) -> None:
        """Click the Add button on the Vacancies list page."""
        expect(self.add_button).to_be_visible()
        self.add_button.click()
        expect(self.vacancy_name_input).to_be_visible()

    # ------------------------------------------------------------------
    # Step 5 – Fill in vacancy details
    # ------------------------------------------------------------------

    def fill_vacancy_form(self, vacancy_data: dict) -> None:
        """Fill every field on the Add Vacancy form with robust fallbacks."""

        # --- Vacancy Name ---
        if "name" in vacancy_data:
            expect(self.vacancy_name_input).to_be_visible()
            self.vacancy_name_input.fill(vacancy_data["name"])
            print(f"Vacancy name entered: {vacancy_data['name']}")

        # --- Job Title (Resilient Selection) ---
        expect(self.job_title_dropdown).to_be_visible()
        self.job_title_dropdown.click()
        
        self.page.wait_for_selector("div[role='listbox']", state="visible")
        
        target_title = vacancy_data.get("job_title")
        job_option = None

        if target_title:
            candidate_option = self.page.get_by_role("option", name=target_title)
            if candidate_option.count() > 0 and candidate_option.first.is_visible():
                job_option = candidate_option.first

        # Fallback to first valid option if specific title is missing/not found
        if not job_option:
            job_option = self.page.locator("div[role='listbox'] div[role='option']").filter(
                has_not_text="-- Select --"
            ).filter(
                has_not_text="No Records Found"
            ).first

        expect(job_option).to_be_visible(timeout=5000)
        job_option.click()

        # --- Description ---
        expect(self.description_textarea).to_be_visible()
        self.description_textarea.fill(vacancy_data.get("description", "Created by Playwright automation"))

        # --- Number of Positions ---
        expect(self.number_of_positions_input).to_be_visible()
        self.number_of_positions_input.fill(str(vacancy_data.get("number_of_positions", 1)))

        # --- Hiring Manager ---
        expect(self.hiring_manager_input).to_be_visible()
        self.hiring_manager_input.fill(vacancy_data["hiring_manager"])

        # Wait until the autocomplete dropdown appears.
        autocomplete_dropdown = self.page.locator(".oxd-autocomplete-dropdown")
        expect(autocomplete_dropdown).to_be_visible(timeout=60000)

        # Wait until at least one suggestion appears.
        manager_option = autocomplete_dropdown.locator(".oxd-autocomplete-option").first
        expect(manager_option).to_be_visible(timeout=60000)

        self.page.wait_for_timeout(2000)

        # Click the visible suggestion.
        manager_option.click()

        print("Vacancy form filled successfully")

    # ------------------------------------------------------------------
    # Step 6 – Click Save
    # ------------------------------------------------------------------

    def save_vacancy(self) -> None:
        """Click Save, handle navigation, and verify success toast."""
        expect(self.save_button).to_be_visible()
        print("Save button is visible.")

        print("Clicking Save...")
        self.save_button.click(no_wait_after=True)
        print("Save clicked.")

        # Verify success toast during the Save transition.
        try:
            save_toast = self.page.get_by_text(
                "Successfully Saved",
                exact=True
            )

            expect(save_toast).to_be_visible(timeout=5000)
            print("Success toast is visible.")

            toast_text = save_toast.inner_text()
            print("================================")
            print("TOAST MESSAGE:", toast_text)
            print("================================")

            expect(toast_text).to_be(
                "Successfully Saved"
            )
            print("Toast message verified successfully.")

        except AssertionError:
            print("Success toast was not visible during the Save transition.")

            # OrangeHRM navigates to the Edit Vacancy page after Save.
            expect(self.page).to_have_url(re.compile(r".*/web/index\.php/recruitment/addJobVacancy/\d+.*"), timeout=15000)
            print("Edit Vacancy page loaded after Save.")

    # ------------------------------------------------------------------
    # Step 8 + 9 – Find vacancy in list
    # ------------------------------------------------------------------

    def verify_vacancy_in_list(self, vacancy_name: str) -> None:
        """Navigate to Vacancies list and verify the row exists."""
        current_url = self.page.url
        print(f"Current URL before vacancy list verification: {current_url}")

        # Always make sure we are on the Vacancies list.
        if "/recruitment/viewJobVacancy" not in current_url:
            print("Navigating to Vacancies list...")
            expect(self.vacancies_link).to_be_visible()
            self.vacancies_link.scroll_into_view_if_needed()
            self.vacancies_link.click()

        # Explicitly verify that navigation reached the Vacancies list.
        expect(self.page).to_have_url(re.compile(r".*/web/index\.php/recruitment/viewJobVacancy.*"), timeout=10000)
        expect(self.vacancies_header).to_be_visible(timeout=10000)

        print("Vacancies list loaded.")

        # Find the exact vacancy row.
        vacancy_row = self.page.get_by_role("row", name=vacancy_name).first
        expect(vacancy_row).to_be_visible(timeout=10000)

        print(f"Vacancy found in list: {vacancy_name}")
        self.save_vacancy_to_file(vacancy_name)

    # ------------------------------------------------------------------
    # Step 10 – Delete the vacancy
    # ------------------------------------------------------------------

    def delete_vacancy(self, vacancy_name: str) -> None:
        """Find the vacancy, click delete, and verify removal."""
        if "/recruitment/viewJobVacancy" not in self.page.url:
            print("Navigating to Vacancies list before deletion...")
            expect(self.vacancies_link).to_be_visible()
            self.vacancies_link.scroll_into_view_if_needed()
            self.vacancies_link.click()

        expect(self.page).to_have_url(re.compile(r".*/web/index\.php/recruitment/viewJobVacancy.*"), timeout=10000)
        expect(self.vacancies_header).to_be_visible(timeout=10000)

        vacancy_row = self.page.get_by_role("row", name=vacancy_name).first
        expect(vacancy_row).to_be_visible(timeout=10000)
        vacancy_row.scroll_into_view_if_needed()

        print(f"Preparing to delete vacancy: {vacancy_name}")

        action_button = vacancy_row.get_by_role("button").first
        expect(action_button).to_be_visible(timeout=5000)
        action_button.scroll_into_view_if_needed()
        expect(action_button).to_be_enabled(timeout=5000)

        print("Delete action button is visible and enabled.")
        action_button.click()
        print("Vacancy action menu opened.")

        delete_menu_item = self.page.get_by_text(" Yes, Delete ", exact=True).last
        expect(delete_menu_item).to_be_visible(timeout=5000)
        print("Delete option is visible.")

        delete_menu_item.click()
        print("Delete option clicked.")

        delete_toast = self.page.get_by_text("Successfully Deleted", exact=True)
        expect(delete_toast).to_be_visible(timeout=10000)

        toast_message = delete_toast.inner_text()
        print(f"Toast message: {toast_message}")

        expect(delete_toast).to_contain_text("Successfully Deleted", timeout=10000)
        print(f"Vacancy deleted successfully: {vacancy_name}")

        expect(self.page.get_by_role("row", name=vacancy_name)).to_have_count(0)
        print(f"Vacancy row removed successfully: {vacancy_name}")

    # ------------------------------------------------------------------
    # Utility – persist vacancy name to file
    # ------------------------------------------------------------------

    def save_vacancy_to_file(self, vacancy_name: str) -> None:
        """Persist the created vacancy name in the vacancy output file."""
        self.output_file.parent.mkdir(parents=True, exist_ok=True)
        self.output_file.write_text(vacancy_name, encoding="utf-8")
        print(f"Vacancy result saved to: {self.output_file}")

    # ------------------------------------------------------------------
    # Complete vacancy flow
    # ------------------------------------------------------------------

    def create_vacancy(self, vacancy_data: dict) -> str:
        """Complete vacancy creation and verification flow."""
        self.click_recruitment()
        self.click_vacancies()
        self.click_add()

        vacancy_data["hiring_manager"] = self.get_logged_in_user_name()
        print(f"Current logged-in user: {vacancy_data['hiring_manager']}")

        self.fill_vacancy_form(vacancy_data)
        self.save_vacancy()
        self.verify_vacancy_in_list(vacancy_data["name"])

        return vacancy_data["name"]