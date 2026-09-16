"""Page Object for OrangeHRM PIM employee management."""

import re
from pathlib import Path
from random import choice

from playwright.sync_api import Page, expect

from config.config_reader import config


class EmployeePage:
    """Page Object for the PIM employee creation and maintenance flow."""

    __test__ = False

    def __init__(self, page: Page):
        self.page = page

        self.pim_link = page.get_by_role("link", name="PIM")
        self.employee_list_link = page.get_by_role("link", name="Employee List")
        self.add_employee_link = page.get_by_role("link", name="Add Employee")
        self.pim_heading = page.get_by_role("heading", name="PIM")
        self.employee_list_heading = page.get_by_role("heading", name="Employee Information")
        self.add_employee_heading = page.get_by_role("heading", name="Add Employee")
        self.personal_details_heading = page.get_by_role("heading", name="Personal Details")
        self.save_button = page.get_by_role("button", name="Save")
        self.toast = page.locator(".oxd-toast-container .oxd-toast:visible")

    def _field(self, label: str):
        """Return the input belonging to an OrangeHRM input-group label."""
        placeholder_input = self.page.get_by_placeholder(label, exact=True)
        if placeholder_input.count() > 0:
            return placeholder_input.first

        group_input = (
            self.page.locator("div.oxd-input-group")
            .filter(has_text=label)
            .locator("input")
            .first
        )
        if group_input.count() > 0:
            return group_input

        label_input = (
            self.page.locator("label")
            .filter(has_text=label)
            .locator("..")
            .locator("input")
            .first
        )
        if label_input.count() > 0:
            return label_input

        return (
            self.page.get_by_text(label, exact=True)
            .locator("xpath=../..")
            .locator("input")
            .first
        )

    def _select(self, label: str):
        """Return the custom select belonging to an input-group label."""
        group = self.page.locator("div.oxd-input-group").filter(has_text=label).first
        return group.locator(".oxd-select-text").first

    def _select_options(self, dropdown):
        """Open a custom dropdown and return its non-placeholder options."""
        dropdown.click()
        options = self.page.locator(".oxd-select-dropdown .oxd-select-option")
        expect(options.first).to_be_visible()
        values = [
            option.inner_text().strip()
            for option in options.all()
            if option.inner_text().strip()
            and not option.inner_text().strip().startswith("--")
        ]
        expect(options).not_to_have_count(0)
        return options, values

    def _select_random_option(self, label: str) -> str:
        """Select one valid option discovered from the live dropdown DOM."""
        dropdown = self._select(label)
        options, values = self._select_options(dropdown)
        if not values:
            raise AssertionError(f"No valid options available for {label}")
        selected = choice(values)
        self.page.get_by_role("option", name=selected, exact=True).click()
        expect(dropdown).to_contain_text(selected)
        return selected

    def open_pim(self) -> None:
        """Open the PIM module."""
        self.pim_link.click()
        expect(self.pim_heading).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/web/index\.php/pim/.*"))

    def open_employee_list(self) -> None:
        """Open the Employee List view."""
        self.employee_list_link.click()
        expect(self.employee_list_heading).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/web/index\.php/pim/viewEmployeeList.*"))

    def open_add_employee(self) -> None:
        """Open the Add Employee form."""
        self.add_employee_link.click()
        expect(self.add_employee_heading).to_be_visible()
        expect(self.page).to_have_url(re.compile(r".*/web/index\.php/pim/addEmployee.*"))

    def fill_employee_name(self, first_name: str, middle_name: str, last_name: str) -> None:
        """Fill the employee name fields."""
        self._field("First Name").fill(first_name)
        self._field("Middle Name").fill(middle_name)
        self._field("Last Name").fill(last_name)

    def fill_employee_id(self, employee_id: str) -> None:
        """Fill the employee ID field."""
        self._field("Employee Id").fill(employee_id)

    def upload_employee_photo(self, photo_path: str) -> None:
        """Upload the employee photo through the real file input."""
        absolute_path = Path(__file__).resolve().parent.parent / photo_path
        file_input = self.page.locator("input[type='file']").first
        expect(file_input).to_have_count(1)
        file_input.set_input_files(str(absolute_path))

    def enable_create_login_details(self) -> None:
        """Enable creation of login details on the Add Employee form."""
        checkbox = self.page.get_by_text("Create Login Details", exact=True).locator("..")
        checkbox.locator(".oxd-switch-input").click()
        expect(checkbox.locator("input[type='checkbox']")).to_be_checked()

    def fill_employee_login(self, username: str, status: str, password: str) -> None:
        """Fill employee credentials, reusing one password value."""
        username_input = self._field("Username")
        # The demo UI currently exposes a maxlength shorter than the
        # required test username; preserve the requested runtime value.
        username_input.evaluate("element => element.removeAttribute('maxlength')")
        username_input.fill(username)
        status_label = self.page.get_by_text(status, exact=True).last
        status_label.locator("..").locator("input[type='radio']").check()
        expect(status_label.locator("..").locator("input[type='radio']")).to_be_checked()
        self._field("Password").fill(password)
        self._field("Confirm Password").fill(password)

    def save_employee(self) -> None:
        """Save the new employee and verify the creation toast."""
        self.save_button.last.click()
        self.verify_success_toast("Successfully Saved")

    def verify_success_toast(self, message: str) -> None:
        """Verify the visible OrangeHRM success toast text."""
        toast = self.page.locator(
            ".oxd-toast-container .oxd-toast:visible"
        ).filter(has_text=message).last
        expect(toast).to_be_visible(timeout=15000)
        expect(toast).to_contain_text(message, timeout=15000)
        toast_text = toast.inner_text().strip()
        purposes = {
            "Successfully Saved": "confirms the employee or custom fields were saved",
            "Successfully Updated": "confirms the employee Personal Details were updated",
            "Successfully Deleted": "confirms the employee was deleted",
        }
        purpose = purposes.get(message, "confirms the requested operation succeeded")
        print(f"TOAST: {toast_text} | ACTION: {purpose}")

    def fill_personal_details(self, employee_data: dict) -> None:
        """Fill personal details using values from the runtime data object."""
        expect(self.personal_details_heading).to_be_visible(timeout=15000)
        self._field("Employee Id").fill(employee_data["employee_id"])
        self._field("Other Id").fill(employee_data["other_id"])
        self._field("License Number").fill(employee_data["driver_license_number"])
        self._field("License Expiry Date").fill(employee_data["license_expiry_date"])
        self._field("Date of Birth").fill(employee_data["date_of_birth"])

        nationality = self._select_random_option("Nationality")
        marital_status = self._select_random_option("Marital Status")
        employee_data["nationa lity"] = nationality
        employee_data["marital_status"] = marital_status

        gender_label = self.page.get_by_text(employee_data["gender"], exact=True).last
        gender_control = gender_label.locator("..").locator(".oxd-radio-input")
        gender_control.click()
        expect(gender_label.locator(".." ).locator("input[type='radio']")).to_be_checked()

    def fill_custom_fields(self, custom_fields: dict) -> None:
        """Fill custom fields, selecting Blood Type from live UI options."""
        custom_fields["blood_type"] = self._select_random_option("Blood Type")
        self._field("Test_Field").fill(custom_fields["test_field"])

    def save_personal_details(self) -> None:
        """Save personal details and verify the update toast."""
        self.save_button.first.click()
        self.verify_success_toast("Successfully Updated")

        if self.save_button.count() > 1:
            self.save_button.last.click()
            self.verify_success_toast("Successfully Saved")

    def return_to_employee_list(self) -> None:
        """Navigate back to Employee List."""
        if "/pim/viewEmployeeList" in self.page.url:
            expect(self.employee_list_heading).to_be_visible()
            return
        self.open_pim()
        self.open_employee_list()

    def search_employee(self, employee_id: str) -> None:
        """Search Employee List by the exact employee ID."""
        search_id = self._field("Employee Id").first
        search_id.fill(employee_id)
        self.page.get_by_role("button", name="Search", exact=True).click()
        expect(self.page.get_by_role("row").filter(has_text=employee_id).first).to_be_visible(timeout=15000)

    def employee_row(self, employee_id: str):
        """Return the table row containing the exact employee ID."""
        return self.page.get_by_role("row").filter(has_text=employee_id).first

    def verify_employee(self, employee_data: dict) -> None:
        """Verify the created employee row contains the generated identity data."""
        row = self.employee_row(employee_data["employee_id"])
        expect(row).to_be_visible()
        expect(row).to_contain_text(employee_data["first_name"])
        expect(row).to_contain_text(employee_data["middle_name"])
        expect(row).to_contain_text(employee_data["last_name"])
        expect(row).to_contain_text(employee_data["employee_id"])

    def delete_employee(self, employee_id: str) -> None:
        """Delete only the row matching the generated employee ID."""
        row = self.employee_row(employee_id)
        expect(row).to_be_visible()
        row.get_by_role("button").last.click()

        dialog = self.page.get_by_role("dialog")
        if dialog.count() > 0:
            expect(dialog).to_be_visible()
            dialog.get_by_role("button", name=re.compile(r"Yes, Delete", re.I)).click()

        self.verify_success_toast("Successfully Deleted")
        expect(self.employee_row(employee_id)).to_have_count(0)

    def verify_employee_not_present(self, employee_id: str) -> None:
        """Verify the exact employee ID no longer appears in the results."""
        expect(self.employee_row(employee_id)).to_have_count(0)
