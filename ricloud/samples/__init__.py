# Keep a register of available sample applications here. The `select_application` utils function look at these.
def get_samples(service):
    from .icloud_sample import SampleICloudApplication
    from .native_sample import SampleICloudNativeApplication

    ALL_APPLICATIONS = [
        SampleICloudApplication,
    ]

    return [application for application in ALL_APPLICATIONS
            if application.client_name.service == service]
