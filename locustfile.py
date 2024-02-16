import random

from locust import HttpUser, task, between

# SITES = ['RBO', 'BV', 'PET', 'HTL', 'FMDE', 'HTLMX', 'CBN', 'OAHU', 'SSR', 'HTL']
SITES = ['RH', 'RBO', 'BV', 'STY', 'OAHU', 'PET', 'SOR', 'SR17', 'ALO', 'EXEC', 'VHR', 'AVI', 'BVAU', 'BVUK',
         'RHDE', 'MLFR', 'ODS', 'SSR', 'HTL', 'VRM', 'BVCA', 'HTLES', 'VAC', 'CBNCA', 'CBN', 'PCT', 'HTLAR', 'HTLMX',
         'FMDE']


class STSUser(HttpUser):
    wait_time = between(5, 15)

    @task
    def sts_test(self):
        site = random.choice(SITES)
        self.client.get(
            f"/api/get-sts-config/?format=json&site={site}"
        )