"""
Admin section configuration.
"""

from django.contrib import admin, messages
from django.contrib.sites.shortcuts import get_current_site
from django.core.management import call_command
from django.utils.html import format_html
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _
from django.urls import reverse

from credentials.apps.badges.admin_forms import (
    BadgePenaltyForm,
    CredlyOrganizationAdminForm,
    DataRuleForm,
    DataRuleFormSet,
)

from credentials.apps.badges.models import (
    BadgePenalty,
    BadgeProgress,
    BadgeRequirement,
    CredlyBadge,
    CredlyBadgeTemplate,
    CredlyOrganization,
    DataRule,
    Fulfillment,
    PenaltyDataRule,
)
from credentials.apps.badges.toggles import is_badges_enabled


class BadgeRequirementInline(admin.TabularInline):
    model = BadgeRequirement
    show_change_link = True
    extra = 0
    fields = ("event_type", "rules", "description")
    readonly_fields = ("rules",)

    # FIXME: disable until "Release VI"
    exclude = [
        "group",
    ]

    def rules(self, obj):
        """
        Display all data rules for the requirement.
        """
        return format_html(
            "<ul>{}</ul>",
            mark_safe(
                "".join(
                    f"<li>{rule.data_path} {rule.OPERATORS[rule.operator]} {rule.value}</li>"
                    for rule in obj.rules.all()
                )
            )
        )


class BadgePenaltyInline(admin.TabularInline):
    model = BadgePenalty
    show_change_link = True
    extra = 0
    form = BadgePenaltyForm

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "requirements":
            template_id = request.resolver_match.kwargs.get("object_id")
            if template_id:
                kwargs["queryset"] = BadgeRequirement.objects.filter(template_id=template_id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)


class FulfillmentInline(admin.TabularInline):
    model = Fulfillment
    extra = 0
    readonly_fields = [
        "requirement",
    ]


class DataRuleInline(admin.TabularInline):
    model = DataRule
    extra = 0
    form = DataRuleForm
    formset = DataRuleFormSet


class CredlyOrganizationAdmin(admin.ModelAdmin):
    """
    Credly organization admin setup.
    """

    form = CredlyOrganizationAdminForm
    list_display = (
        "name",
        "uuid",
        "api_key",
    )
    readonly_fields = [
        "name",
    ]
    actions = ("sync_organization_badge_templates",)

    @admin.action(description="Sync organization badge templates")
    def sync_organization_badge_templates(self, request, queryset):
        """
        Sync badge templates for selected organizations.
        """
        site = get_current_site(request)
        for organization in queryset:
            call_command(
                "sync_organization_badge_templates",
                organization_id=organization.uuid,
                site_id=site.id,
            )

        messages.success(request, _("Badge templates were successfully updated."))


class CredlyBadgeTemplateAdmin(admin.ModelAdmin):
    """
    Badge template admin setup.
    """

    exclude = [
        "icon",
    ]
    list_display = (
        "organization",
        "state",
        "name",
        "uuid",
        "is_active",
        "image",
    )
    list_filter = (
        "organization",
        "is_active",
        "state",
    )
    search_fields = (
        "name",
        "uuid",
    )
    readonly_fields = [
        "organization",
        "origin",
        "state",
        "dashboard_link",
        "image",
    ]
    fieldsets = (
        (
            "Generic",
            {
                "fields": (
                    "site",
                    "is_active",
                ),
                "description": _(
                    """
                    WARNING: avoid configuration updates on activated badges.
                    Active badge templates are continuously processed and learners may already have partial progress on them.
                    Any changes in badge template requirements (including data rules) will affect learners' experience!
                    """
                ),
            },
        ),
        (
            "Badge template",
            {
                "fields": (
                    "uuid",
                    "name",
                    "description",
                    "image",
                    "origin",
                )
            },
        ),
        (
            "Credly",
            {
                "fields": (
                    "organization",
                    "state",
                    "dashboard_link",
                ),
            },
        ),
    )
    inlines = [
        BadgeRequirementInline,
        # FIXME: disable until "Release V"
        # BadgePenaltyInline,
    ]

    def has_add_permission(self, request):
        return False

    def dashboard_link(self, obj):
        url = obj.management_url
        return format_html("<a href='{url}'>{url}</a>", url=url)

    def delete_model(self, request, obj):
        """
        Prevent deletion of active badge templates.
        """
        if obj.is_active:
            messages.set_level(request, messages.ERROR)
            messages.error(request, "Active badge template cannot be deleted.")
            return
        super().delete_model(request, obj)

    def delete_queryset(self, request, queryset):
        """
        Prevent deletion of active badge templates.
        """
        if queryset.filter(is_active=True).exists():
            messages.set_level(request, messages.ERROR)
            messages.error(request, "Active badge templates cannot be deleted.")
            return
        super().delete_queryset(request, queryset)

    def image(self, obj):
        """
        Badge template preview image.
        """
        if obj.icon:
            return format_html('<img src="{}" width="50" height="auto" />', obj.icon)
        return None

    image.short_description = _("icon")

    def save_related(self, request, form, formsets, change):
        """
        Save inline forms before checking for existence of requirements.
        """
        for formset in formsets:
            self.save_formset(request, form, formset, change)

        obj = form.instance
        if obj.is_active and not obj.requirements.exists():
            messages.set_level(request, messages.ERROR)
            messages.error(request, "Badge Template must have at least 1 Requirement set.")
            return
        super().save_related(request, form, formsets, change)


class DataRulePenaltyInline(admin.TabularInline):
    model = PenaltyDataRule
    extra = 0


class BadgeRequirementAdmin(admin.ModelAdmin):
    """
    Badge template requirement admin setup.
    """

    inlines = [
        DataRuleInline,
    ]

    list_display = [
        "id",
        "__str__",
        "event_type",
        "template_link",
    ]
    list_display_links = (
        "id",
        "__str__",
    )
    list_filter = [
        "template",
        "event_type",
    ]
    readonly_fields = [
        "template",
        "event_type",
        "template_link",
    ]

    fields = [
        "template_link",
        "event_type",
        "description",
        # FIXME: disable until "Release VI"
        # "group",
    ]

    def has_add_permission(self, request):
        return False

    def template_link(self, instance):
        """
        Interactive link to parent (badge template).
        """
        url = reverse("admin:badges_credlybadgetemplate_change", args=[instance.template.pk])
        return format_html('<a href="{}">{}</a>', url, instance.template)

    template_link.short_description = _("badge template")


class BadgePenaltyAdmin(admin.ModelAdmin):
    """
    Badge requirement penalty setup admin.
    """

    inlines = [
        DataRulePenaltyInline,
    ]

    list_display_links = (
        "id",
        "template",
    )
    list_display = [
        "id",
        "__str__",
        "event_type",
        "template_link",
    ]
    list_display_links = (
        "id",
        "__str__",
    )
    list_filter = [
        "template",
        "requirements",
    ]
    form = BadgePenaltyForm

    def has_add_permission(self, request):
        return False

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "requirements":
            template_id = request.resolver_match.kwargs.get("object_id")
            if template_id:
                kwargs["queryset"] = BadgeRequirement.objects.filter(template_id=template_id)
        return super().formfield_for_manytomany(db_field, request, **kwargs)

    def template_link(self, instance):
        """
        Interactive link to parent (badge template).
        """
        url = reverse("admin:badges_credlybadgetemplate_change", args=[instance.template.pk])
        return format_html('<a href="{}">{}</a>', url, instance.template)

    template_link.short_description = _("badge template")


class BadgeProgressAdmin(admin.ModelAdmin):
    """
    Badge template progress admin setup.
    """

    inlines = [
        FulfillmentInline,
    ]
    list_display = [
        "id",
        "username",
        "template",
        "complete",
    ]
    list_display_links = (
        "id",
        "username",
        "template",
    )
    readonly_fields = (
        "username",
        "template",
        "complete",
        "ratio",
    )

    @admin.display(boolean=True)
    def complete(self, obj):
        """
        Identifies if all requirements are already fulfilled.

        NOTE: (performance) dynamic evaluation.
        """
        return obj.completed

    def ratio(self, obj):
        """
        Displays progress value.
        """
        return obj.ratio

    def has_add_permission(self, request):
        return False


class CredlyBadgeAdmin(admin.ModelAdmin):
    """
    Credly badge admin setup.
    """

    list_display = (
        "uuid",
        "username",
        "credential",
        "status",
        "state",
        "external_uuid",
    )
    list_filter = (
        "status",
        "state",
    )
    search_fields = (
        "username",
        "external_uuid",
    )
    readonly_fields = (
        "credential_id",
        "credential_content_type",
        "username",
        "download_url",
        "state",
        "uuid",
        "external_uuid",
    )

    def has_add_permission(self, request):
        return False


# register admin configurations with respect to the feature flag
if is_badges_enabled():
    admin.site.register(CredlyOrganization, CredlyOrganizationAdmin)
    admin.site.register(CredlyBadgeTemplate, CredlyBadgeTemplateAdmin)
    admin.site.register(CredlyBadge, CredlyBadgeAdmin)
    admin.site.register(BadgeRequirement, BadgeRequirementAdmin)
    # FIXME: disable until "Release V"
    # admin.site.register(BadgePenalty, BadgePenaltyAdmin)
    admin.site.register(BadgeProgress, BadgeProgressAdmin)
