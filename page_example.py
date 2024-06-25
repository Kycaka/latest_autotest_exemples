import allure

from selenium.common.exceptions import NoSuchElementException
from client.selenium_web_client.driver_function import Locator
from client.selenium_web_client.block import Block
from pages.mc.panels.edit_page_tabs_panel import EditPageTabsPanel
from pages.mc.panels.main_action_bar import MainActionsBar
from pages.mc.panels.main_edit_page_bar import MainEditPageBar
from pages.mc.accounts.dialogs.add_account_dialog import AddAccountDialog
from pages.mc.accounts.edit_account_page import EditAccountPage
from pages.mc.dialog_windows.confirm_dialog import ConfirmDialog


class McAccountsPage:
    main_actions_bar = MainActionsBar()
    main_edit_page_bar = MainEditPageBar()
    add_account = AddAccountDialog()
    edit_account = EditAccountPage()
    confirm_dialog = ConfirmDialog()
    edit_page_tabs_panel = EditPageTabsPanel()

    accounts_table_all = Block('Result item', 'tbody > tr > td')
    block_warning_alert = Locator('app-alert-warning')
    no_accounts_message = Locator('[class="hide-when-empty app-callout app-callout-info"]')
    account_warning_message = Locator('app-alert-warning div > div')

    def choose_account(self, account_name, state=None, **kwargs):
        with allure.step(f'Выбор УЗ {account_name}'):
            if state:
                self.main_actions_bar.advanced_search.click()
                self.main_actions_bar.account_state.select(state)
            self.main_actions_bar.search_text_field.input(account_name)
            self.main_actions_bar.search_button.click(wait_for_loader_off=True)
            if kwargs.__len__() != 0:
                if kwargs.get('domain_name'):
                    self.accounts_table_all.click_in_element_block(f'{kwargs.get("domain_name")}\\{account_name}')
                if kwargs.get('resource_name'):
                    self.accounts_table_all.click_in_element_block(f'{kwargs.get("resource_name")}\\{account_name}')
                self.accounts_table_all.click_in_element_block(account_name)
            else:
                self.edit_account.accounts_table_elements.get_all_blocks()[0].title.click()

    def check_account_is_removed(self, account_name):
        with allure.step('Удаление УЗ'):
            self.main_edit_page_bar.remove.click()
            self.add_account.next.click()
            self.main_actions_bar.search_text_field.input(account_name)
            self.main_actions_bar.search_button.click()
            assert self.no_accounts_message.text() == 'Нет учетных записей', 'Account was not removed'

    def make_account_manageable(self, **kwargs):
        """
        Makes any account manageable, if method receive variable "account_is_placed_on_linux_resource", makes one more
        click on button next.
        """
        try:
            if 'Учетная запись ожидает решения' == self.account_warning_message.text():
                self.main_edit_page_bar.manage_account.click(wait_for_loader_off=True)
                if kwargs.get('set_password_manualy'):
                    incorrect_password = 'Old_password'
                    self.edit_account.change_password(password_manual=True, password=incorrect_password,
                                                      password_confirm=incorrect_password)
                else:
                    self.edit_account.change_password(password_generate=True)
                self.add_account.next.click(wait_for_loader_off=True)
                if kwargs.get('account_is_placed_on_linux_resource'):
                    self.add_account.next.click(wait_for_loader_off=True)
        except NoSuchElementException:
            print('Account is already managed')

    def change_status_account(self, **kwargs):
        actions = {
            'block': self.main_edit_page_bar.block,
            'ignore': self.main_edit_page_bar.ignore,
            'delete': self.main_edit_page_bar.remove
        }

        for action, element in actions.items():
            if kwargs.get(action):
                element.click()

        self.confirm_dialog.confirm.click()
        self.confirm_dialog.confirm.wait_for_disappear()
        self.confirm_dialog.close.click()
        self.confirm_dialog.close.wait_for_disappear()

    def check_exists_block_with_warning_message(self, text, enter_account=True):
        if enter_account:
            self.edit_account.accounts_table_elements.get_all_blocks()[0].title.click()
            self.block_warning_alert.wait_for_displayed()
        res = self.block_warning_alert.text()
        assert res == text, 'Warning alert text is incorrect.'

    def check_state_account(self, account_name, state):
        self.main_actions_bar.search_text_field.input(account_name)
        self.main_actions_bar.search_button.click(wait_for_loader_off=True)
        results = self.edit_account.accounts_table_elements.transform_block_elements_into_text_list()
        result = [state for sublist in results if state in sublist]
        assert result, f'The selected account: - {account_name} isn\'t wait issue state.'
