from django.contrib import admin
from django.contrib.auth import get_user_model
from django.db.models import Count, Q

from .models import (  # @@@ make all these read-only
    Charge,
    Subscription,
    Card,
    BitcoinReceiver,
    Customer,
    Event,
    EventProcessingException,
    Invoice,
    InvoiceItem,
    Plan,
    Coupon,
    Transfer,
    TransferChargeFee,
    Product,
    Sku,
    Order
)


def user_search_fields():  # coverage: omit
    User = get_user_model()
    fields = [
        "user__{0}".format(User.USERNAME_FIELD)
    ]
    if "email" in [f.name for f in User._meta.fields]:
        fields += ["user__email"]
    return fields


def customer_search_fields():
    return [
        "customer__{0}".format(field)
        for field in user_search_fields()
    ]


class CustomerHasCardListFilter(admin.SimpleListFilter):
    title = "card presence"
    parameter_name = "has_card"

    def lookups(self, request, model_admin):
        return [
            ["yes", "Has Card"],
            ["no", "Does Not Have a Card"]
        ]

    def queryset(self, request, queryset):
        no_card = Q(card__fingerprint="") | Q(card=None)
        if self.value() == "yes":
            return queryset.exclude(no_card)
        elif self.value() == "no":
            return queryset.filter(no_card)
        return queryset.all()


class InvoiceCustomerHasCardListFilter(admin.SimpleListFilter):
    title = "card presence"
    parameter_name = "has_card"

    def lookups(self, request, model_admin):
        return [
            ["yes", "Has Card"],
            ["no", "Does Not Have a Card"]
        ]

    def queryset(self, request, queryset):
        no_card = (Q(customer__card__fingerprint="") | Q(customer__card=None))
        if self.value() == "yes":  # coverage: omit
            # Worked when manually tested, getting a weird error otherwise
            # Better than no tests at all
            return queryset.exclude(no_card)
        elif self.value() == "no":
            return queryset.filter(no_card)
        return queryset.all()


class CustomerSubscriptionStatusListFilter(admin.SimpleListFilter):
    title = "subscription status"
    parameter_name = "sub_status"

    def lookups(self, request, model_admin):
        statuses = [
            [x, x.replace("_", " ").title()]
            for x in Subscription.objects.all().values_list(
                "status",
                flat=True
            ).distinct()
        ]
        statuses.append(["none", "No Subscription"])
        return statuses

    def queryset(self, request, queryset):
        if self.value() == "none":
            # Get customers with 0 subscriptions
            return queryset.annotate(subs=Count('subscription')).filter(subs=0)
        elif self.value():
            # Get customer pks without a subscription with this status
            customers = Subscription.objects.filter(
                status=self.value()).values_list(
                'customer', flat=True).distinct()
            # Filter by those customers
            return queryset.filter(pk__in=customers)
        return queryset.all()


admin.site.register(
    Charge,
    list_display=[
        "stripe_id",
        "customer",
        "amount",
        "description",
        "paid",
        "disputed",
        "refunded",
        "receipt_sent",
        "created_at"
    ],
    search_fields=[
        "stripe_id",
        "customer__stripe_id",
        "invoice__stripe_id"
    ] + customer_search_fields(),
    list_filter=[
        "paid",
        "disputed",
        "refunded",
        "created_at"
    ],
    raw_id_fields=[
        "customer",
        "invoice"
    ],
)

admin.site.register(
    EventProcessingException,
    list_display=[
        "message",
        "event",
        "created_at"
    ],
    search_fields=[
        "message",
        "traceback",
        "data"
    ],
    raw_id_fields=[
        "event"
    ],
)

admin.site.register(
    Event,
    raw_id_fields=["customer"],
    list_display=[
        "stripe_id",
        "kind",
        "livemode",
        "valid",
        "processed",
        "created_at"
    ],
    list_filter=[
        "kind",
        "created_at",
        "valid",
        "processed"
    ],
    search_fields=[
        "stripe_id",
        "customer__stripe_id",
        "validated_message"
    ] + customer_search_fields(),
)


class SubscriptionInline(admin.TabularInline):
    model = Subscription
    extra = 0
    max_num = 0


class CardInline(admin.TabularInline):
    model = Card
    extra = 0
    max_num = 0


class BitcoinReceiverInline(admin.TabularInline):
    model = BitcoinReceiver
    extra = 0
    max_num = 0


def subscription_status(obj):
    return ", ".join([subscription.status for subscription in obj.subscription_set.all()])
subscription_status.short_description = "Subscription Status"


admin.site.register(
    Customer,
    raw_id_fields=["user"],
    list_display=[
        "stripe_id",
        "user",
        "account_balance",
        "currency",
        "delinquent",
        "default_source",
        subscription_status,
        "date_purged"
    ],
    list_filter=[
        "delinquent",
        CustomerHasCardListFilter,
        CustomerSubscriptionStatusListFilter
    ],
    search_fields=[
        "stripe_id",
    ] + user_search_fields(),
    inlines=[
        SubscriptionInline,
        CardInline,
        BitcoinReceiverInline
    ]
)


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    max_num = 0


def customer_has_card(obj):
    return obj.customer.card_set.exclude(fingerprint='').exists()
customer_has_card.short_description = "Customer Has Card"


def customer_user(obj):
    User = get_user_model()
    username = getattr(obj.customer.user, User.USERNAME_FIELD)
    email = getattr(obj, "email", "")
    return "{0} <{1}>".format(
        username,
        email
    )
customer_user.short_description = "Customer"


admin.site.register(
    Invoice,
    raw_id_fields=["customer"],
    list_display=[
        "stripe_id",
        "paid",
        "closed",
        customer_user,
        customer_has_card,
        "period_start",
        "period_end",
        "subtotal",
        "total"
    ],
    search_fields=[
        "stripe_id",
        "customer__stripe_id",
    ] + customer_search_fields(),
    list_filter=[
        InvoiceCustomerHasCardListFilter,
        "paid",
        "closed",
        "attempted",
        "attempt_count",
        "created_at",
        "date",
        "period_end",
        "total"
    ],
    inlines=[
        InvoiceItemInline
    ]
)

admin.site.register(
    Plan,
    list_display=[
        "stripe_id",
        "name",
        "amount",
        "currency",
        "interval",
        "interval_count",
        "trial_period_days",
    ],
    search_fields=[
        "stripe_id",
        "name",
    ],
    list_filter=[
        "currency",
    ],
    readonly_fields=[
        "stripe_id",
        "name",
        "amount",
        "currency",
        "interval",
        "interval_count",
        "trial_period_days",
        "statement_descriptor",
        "created_at",
    ],
)


admin.site.register(
    Coupon,
    list_display=[
        "stripe_id",
        "amount_off",
        "currency",
        "percent_off",
        "duration",
        "duration_in_months",
        "redeem_by",
        "valid"
    ],
    search_fields=[
        "stripe_id",
    ],
    list_filter=[
        "currency",
        "valid",
    ],
    readonly_fields=[
        "stripe_id",
        "amount_off",
        "currency",
        "duration",
        "duration_in_months",
        "max_redemptions",
        "metadata",
        "percent_off",
        "redeem_by",
        "times_redeemed",
        "valid",
        "created_at"
    ],
)


class TransferChargeFeeInline(admin.TabularInline):
    model = TransferChargeFee
    extra = 0
    max_num = 0


admin.site.register(
    Transfer,
    raw_id_fields=["event"],
    list_display=[
        "stripe_id",
        "amount",
        "status",
        "date",
        "description"
    ],
    search_fields=[
        "stripe_id",
        "event__stripe_id",
        "description"
    ],
    inlines=[
        TransferChargeFeeInline
    ]
)

class SkuInline(admin.TabularInline):
    model = Sku
    extra = 0
    max_num = 0
    readonly_fields = ["stripe_id"]

admin.site.register(
    Product,
    readonly_fields=[
        "stripe_id",
        "created_at",
        "livemode"
    ],
    list_display=[
        "stripe_id",
        "name",
        "caption",
        "description",
        "active",
        "created_at"
    ],
    search_fields=[
        "stripe_id",
        "name",
        "description",
    ],
    inlines=[
        SkuInline
    ]
)

class SkuAdmin(admin.ModelAdmin):
    model = Sku
    raw_id_fields = [
        "product"
    ]

    readonly_fields = [
        "stripe_id",
        "created_at",
        "livemode"
    ]

    list_display = [
        "stripe_id",
        "product_name",
        "image",
        "inventory",
        "active",
        "created_at"
    ]

    search_fields = [
        "stripe_id",
        "product__name",
        "product__description"
    ]

    def product_name(self, obj):
        return obj.product.name

admin.site.register(Sku,SkuAdmin)

class OrderAdmin(admin.ModelAdmin):
    model = Order
    raw_id_fields = [
        "customer"
    ]

    readonly_fields = [
        "stripe_id",
        "created_at",
        "charge",
        "livemode"
    ]

    list_display = [
        "stripe_id",
        "customer_name",
        "amount",
        "currency",
        "status",
        "created_at"
    ]

    search_fields = [
        "stripe_id",
        "amount",
        "customer__user__first_name",
        "customer__user__last_name"
    ]

    def customer_name(self, obj):
        return "%s %s" % (obj.customer.user.first_name, obj.customer.user.first_name)

admin.site.register(Order,OrderAdmin)