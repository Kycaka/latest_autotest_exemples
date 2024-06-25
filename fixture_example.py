@pytest.fixture
def web_uc():
    make_database_dump()

    options = webdriver.ChromeOptions()

    if operation_system != 'win32':
        options.add_argument("--headless")
        options.add_argument('--no-sandbox')

    capabilities = options.to_capabilities()
    capabilities.update({"timeouts": {"implicit": 10000}, "acceptInsecureCerts": True})

    driver = Driver(desired_capabilities=capabilities, executable_path=CONF.Browsers.browser_chrome)

    driver.maximize_window()

    driver.get(CONF.Pages.page_uc)
    WebDriverWait(driver, CONF.Timeouts.sec_10)

    web_driver_client = Application(driver)

    web_driver_client.inter_page_function.login_in_app(CONF.Logins.standard_login, CONF.Passwords.standard_password)

    yield web_driver_client

    restore_database_from_dump()

    driver.quit()