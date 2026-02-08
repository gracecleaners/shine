from django.core.management.base import BaseCommand
from catalog.models import DeliveryZone
from decimal import Decimal


class Command(BaseCommand):
    help = 'Creates sample delivery zones for the shop'

    def handle(self, *args, **options):
        zones = [
            {
                'name': 'Nairobi CBD',
                'description': 'Central Business District and immediate surroundings',
                'base_fee': Decimal('200.00'),
                'per_kg_fee': Decimal('0.00'),
                'estimated_days_min': 1,
                'estimated_days_max': 2,
                'min_order_free_delivery': Decimal('5000.00'),
                'display_order': 1,
            },
            {
                'name': 'Nairobi Metro',
                'description': 'Greater Nairobi area including Westlands, Kilimani, Upperhill, etc.',
                'base_fee': Decimal('300.00'),
                'per_kg_fee': Decimal('0.00'),
                'estimated_days_min': 1,
                'estimated_days_max': 3,
                'min_order_free_delivery': Decimal('7500.00'),
                'display_order': 2,
            },
            {
                'name': 'Nairobi Outskirts',
                'description': 'Outer Nairobi including Rongai, Kitengela, Ruiru, etc.',
                'base_fee': Decimal('450.00'),
                'per_kg_fee': Decimal('0.00'),
                'estimated_days_min': 2,
                'estimated_days_max': 4,
                'min_order_free_delivery': Decimal('10000.00'),
                'display_order': 3,
            },
            {
                'name': 'Major Towns',
                'description': 'Mombasa, Kisumu, Nakuru, Eldoret, Nyeri, and other major towns',
                'base_fee': Decimal('600.00'),
                'per_kg_fee': Decimal('50.00'),
                'estimated_days_min': 3,
                'estimated_days_max': 5,
                'min_order_free_delivery': Decimal('15000.00'),
                'display_order': 4,
            },
            {
                'name': 'Rest of Kenya',
                'description': 'All other locations within Kenya',
                'base_fee': Decimal('800.00'),
                'per_kg_fee': Decimal('75.00'),
                'estimated_days_min': 4,
                'estimated_days_max': 7,
                'min_order_free_delivery': Decimal('20000.00'),
                'display_order': 5,
            },
        ]

        created_count = 0
        for zone_data in zones:
            zone, created = DeliveryZone.objects.get_or_create(
                name=zone_data['name'],
                defaults=zone_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created delivery zone: {zone.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Delivery zone already exists: {zone.name}')
                )

        self.stdout.write(
            self.style.SUCCESS(f'\nDone! Created {created_count} delivery zones.')
        )
