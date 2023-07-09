from django.apps import apps
from django.test.runner import DiscoverRunner


class UnitTestRunner(DiscoverRunner):
    def setup_test_environment(self, **kwargs):
        self.unmanaged_model = [
            m for m in apps.get_models() if m._meta.managed == False
        ]
        for m in self.unmanaged_model:
            m._meta.managed = True
        super(UnitTestRunner, self).setup_test_environment(**kwargs)

    def teardown_test_environment(self, **kwargs):
        super(UnitTestRunner, self).teardown_test_environment(**kwargs)
        for m in self.unmanaged_model:
            m._meta.managed = False
