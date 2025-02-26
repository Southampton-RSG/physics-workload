# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
Modified 2025 - Sam Mangham, Southampton RSG
"""

from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.shortcuts import render, get_object_or_404, redirect
from django.template import loader
from django.http import HttpResponse, JsonResponse, QueryDict
from django import template
from django.template.loader import render_to_string
from django.urls import reverse
from django.views import View
from django.contrib import messages

from app.forms.academic_group import AcademicGroupForm
from app.models import AcademicGroup, Unit
from app.utils import set_pagination


class AcademicGroupView(View):
    context = {'segment': 'academic_groups'}

    def get(self, request, pk=None, action=None):
        if request.is_ajax():
            if pk and action == 'edit':
                edit_row = self.edit_row(pk)
                return JsonResponse({'edit_row': edit_row})
            elif pk and not action:
                edit_row = self.get_row_item(pk)
                return JsonResponse({'edit_row': edit_row})

        if pk and action == 'edit':
            context, template = self.edit(request, pk)
        else:
            context, template = self.list(request)

        if not context:
            html_template = loader.get_template('page-500.html')
            return HttpResponse(html_template.render(self.context, request))

        return render(request, template, context)

    def post(self, request, pk=None, action=None):
        self.update_instance(request, pk)
        return redirect('academic_group')

    def put(self, request, pk, action=None):
        is_done, message = self.update_instance(request, pk, True)
        edit_row = self.get_row_item(pk)
        return JsonResponse({'valid': 'success' if is_done else 'warning', 'message': message, 'edit_row': edit_row})

    def delete(self, request, pk, action=None):
        transaction = self.get_object(pk)
        transaction.delete()

        redirect_url = None
        if action == 'single':
            messages.success(request, 'Item deleted successfully')
            redirect_url = reverse('academic_group')

        response = {'valid': 'success', 'message': 'Item deleted successfully', 'redirect_url': redirect_url}
        return JsonResponse(response)

    """ Get pages """

    def list(self, request):
        filter_params = None

        search = request.GET.get('search')
        if search:
            filter_params = None
            for key in search.split():
                if key.strip():
                    if not filter_params:
                        filter_params = Q(name__icontains=key.strip())
                    else:
                        filter_params |= Q(name__icontains=key.strip())

        objects = AcademicGroup.objects.filter(filter_params) if filter_params else AcademicGroup.objects.all()

        self.context['objects'], self.context['info'] = set_pagination(request, objects)
        if not self.context['objects']:
            return False, self.context['info']

        return self.context, 'app/academic_group/list.html'

    def edit(self, request, pk):
        object = self.get_object(pk)
        self.context['object'] = object
        self.context['form'] = AcademicGroupForm(instance=object)

        return self.context, 'app/academic_group/edit.html'

    """ Get Ajax pages """

    def edit_row(self, pk):
        object = self.get_object(pk)
        form = AcademicGroupForm(instance=object)
        context = {'instance': object, 'form': form}
        return render_to_string('app/academic_group/edit_row.html', context)

    """ Common methods """

    def get_object(self, pk):
        object = get_object_or_404(AcademicGroup, id=pk)
        return object

    def get_row_item(self, pk):
        object = self.get_object(pk)
        edit_row = render_to_string('app/academic_group/edit_row.html', {'instance': object})
        return edit_row

    def update_instance(self, request, pk, is_urlencode=False):
        object = self.get_object(pk)
        form_data = QueryDict(request.body) if is_urlencode else request.POST
        form = AcademicGroupForm(form_data, instance=object)
        if form.is_valid():
            form.save()
            if not is_urlencode:
                messages.success(request, 'Academic Group saved successfully')

            return True, 'Academic Group saved successfully'

        else:
            print(form.errors)


        if not is_urlencode:
            messages.warning(request, 'Error Occurred. Please try again.')
        return False, 'Error Occurred. Please try again.'
