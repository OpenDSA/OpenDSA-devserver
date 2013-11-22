from django import forms
from django.forms import MultipleChoiceField
from django.forms.widgets import Select, CheckboxSelectMultiple
from opendsa.models import Assignments, Books, Exercise, BookModuleExercise
from django.contrib import admin
from django.utils.safestring import mark_safe
from opendsa.models import UserBook

from exercise.exercise_models import  CourseModule
import settings

# Widget
class CSICheckboxSelectMultiple(CheckboxSelectMultiple):
    def value_from_datadict(self, data, files, name):
        # Return a string of comma separated integers since the database, and
        # field expect a string (not a list).
        name = 'id_assignment_exercises' 
        return ','.join(data.getlist(name)).encode('ascii','ignore')

    def render(self, name, value, attrs=None, choices=()):
        # Convert comma separated integer string to a list, since the checkbox
        # rendering code expects a list (not a string)
        if value:
            value.encode('ascii','ignore')
            value = value.split(',')
        js = """
             <script type="text/javascript">
             function fillChapters(course,book){
               $.getJSON('%(path)s' + course + '.json', function(data) {
                 $('#id_assignment_chapter').empty();
                 $.each(data, function(key0, val0) {
                     $.each(val0, function(key1, val1) {
                       $.each(val1, function(key2, val2) {
                         chap = key2.split("-")[0];
                         chap_id = key2.split("-")[1];
                             $('#id_assignment_chapter').append('<option selected="selected" value="'+chap_id+'">'+chap+'</option>');
                       });
                     });
                 });                          
               });
             }
             var selected = [];
             var selected_id = [];
             var val_displayed = [];
             var j = 0;
             function fillExercises(course,book,chapter){
               j = 0;
               var displayed =[];
               $.getJSON('%(path)s' + course + '.json', function(data) {
                     $('#chapter-exercises').empty();
                     $.each(data, function(key0, val0) {
                       $.each(val0, function(key1, val1) {
                         $.each(val1, function(key2, val2) {
                           if(key2.split("-")[1]==chapter){   
                             $.each(val2, function(key, val) {
                               var checked ="";
                               if(jQuery.inArray(key,selected) != -1){
                                 //checkbox checked
                                 displayed.push(jQuery.inArray(key,selected));
                                 checked ="checked";
                               };
                               $('#chapter-exercises').append('<li><label class="id_chapter_exercises" for="id_chapter_exercises_'+j+'"><input id="id_chapter_exercises_'+j+'" class="chapter_exercises" type="checkbox" value="'+key+'" name="chapter_exercises"'+checked+'>'+val+'</label></li>');
                               val_displayed.push(val);
                               j++;
                             });
                           }
                       });
                     });
                 });
               });
               //display checked exercises of the assignement
               $('#exercises-checkbox').empty();
               $.each(selected, function(i,l){
                 if(jQuery.inArray(i,displayed) == -1){
                   $('#exercises-checkbox').append('<li><label for="id_assignment_exercises_'+j+'"><input id="id_assignment_exercises_'+j+'" class="exercises-checkbox" type="checkbox" value="'+l+'" name="id_assignment_exercises" checked="" >'+selected_id[i]+'</label></li>');
                   j++;  
                 };
               });
             } 
             function updateExercises(chapter_exercises){
               $.each(chapter_exercises, function(k, v) {
                 var x = -1;
                 $('.exercises-checkbox').each(function(){
                   if($(this).val()==k.split("-")[0]){
                     x = 1;
                     if(!v){
                       $(this).remove();
                     }
                   }
                 });
                 if (v && (x==-1)){
                   $('#exercises-checkbox').append('<li><label for="id_assignment_exercises_'+j+'"><input id="id_assignment_exercises_'+j+'" class="exercises-checkbox" type="checkbox" value="'+k.split("-")[0]+'" name="id_assignment_exercises" checked="" >'+k.split("-")[1]+'</label></li>');
                   selected.push(k.split("-")[0]);
                   selected_id.push(k.split("-")[1]);
                 }
               });
             } 
             (function($) {
                $(document).ready(function(){
                   //get selected exercises (if any)
                   $(':checkbox:checked').each(function(i){
                     selected[i] = $(this).val();
                     selected_id[i] = $(this).parent().text();
                   });
                   $('#exercises-checkbox').empty();
                   //var course = $("h1").text().split(" ")[1];
                   var course = $('#book-name').attr('data-name');
                   //add chapter select box
                   $('#id_assignment_book').after('<p><label for="id_assignment_chapter">Assignment chapter:</label><select id="id_assignment_chapter" name="assignment_chapter"></select></p>');
                   //add book chapter checkboxes
                   $('#id_assignment_chapter').after('<p id="chapter-exe-label"><label for="chapter-exercises">Exercises in chapter:</label></p><ul id="chapter-exercises"></ul>');
                   //we only display book associated with the course
                   $.getJSON('%(path)s' + course + '.json', function(data) {
                     $('#id_assignment_book').empty();
                     $.each(data, function(key0, val0) {
                       $.each(val0, function(key, val) {
                         text = key.split("-")[0];
                         value = key.split("-")[1];
                         $('#id_assignment_book').append('<option selected="selected" value="'+value+'">'+text+'</option>');
                           $.each(val, function(key1, val1) {
                             chap = key1.split("-")[0];
                             chap_id = key1.split("-")[1];
                             $('#id_assignment_chapter').append('<option selected="selected" value="'+chap_id+'">'+chap+'</option>'); 
                           });
                       });
                     });
                   });
                   fillExercises( course, $('#id_assignment_book').val(), $('#id_assignment_chapter').val());
                   $('#exercises-checkbox').empty();
                   $('#id_assignment_book').change(function(){
                     fillChapters( course, $('#id_assignment_book').val());
                   });
                   $('#id_assignment_chapter').change(function(){
                     fillExercises( course, $('#id_assignment_book').val(), $('#id_assignment_chapter').val());
                   });
                   //we add selected chapter exercises to assignment exercises
                   $('.chapter_exercises').live('change',function(){
                     var checked_dict = {};
                     $(':checkbox:checked.chapter_exercises').each(function(){
                       var id_text = $(this).val() + '-' +$(this).parent().text();
                       checked_dict[id_text]= true;//$(this).parent().text();
                     });
                     $(':checkbox:not(:checked).chapter_exercises').each(function(){
                       var id_text = $(this).val() + '-' +$(this).parent().text();
                       checked_dict[id_text]= false;//$(this).parent().text();
                     });
                     updateExercises(checked_dict);
                   });
                })
             })(jQuery);
             </script>
             """
        js = js % {"path": settings.MEDIA_URL }
        output = super(CSICheckboxSelectMultiple, self).render(
            name, value, attrs=attrs, choices=choices
        )
        output = output.replace('<ul>','<ul id= "exercises-checkbox">')
        output += js
        return mark_safe(output)

# Form field
class CSIMultipleChoiceField(MultipleChoiceField):
    widget = CSICheckboxSelectMultiple

    # Value is stored and retrieved as a string of comma separated
    # integers. We don't want to do processing to convert the value to
    # a list like the normal MultipleChoiceField does.
    def to_python(self, value):
        return value

    def validate(self, value):
        # If we have a value, then we know it is a string of comma separated
        # integers. To use the MultipleChoiceField validator, we first have
        # to convert the value to a list.
        if value:
            value.encode('ascii','ignore')
            value = value.split(',')
        super(CSIMultipleChoiceField, self).validate(value)


def exercises_in_book(book=None):
    a_exe = Exercise.objects.all()
    result = ()
    for exe in a_exe:
       if not exe.name.isspace():
          result += ((exe.id,exe.name),)
    return result


class AssignmentForm(forms.ModelForm):
    assignment_exercises = CSIMultipleChoiceField( choices =exercises_in_book(), # settings.exercises_in_book, #all_exercises(),
        required=False,
    )

    class Meta:
        model = Assignments 

class AssignmentAdmin(admin.ModelAdmin):
    form = AssignmentForm


class StudentsForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super(StudentsForm, self).__init__(*args, **kwargs)
        instance = getattr(self, 'instance', None)
        if instance:
            self.fields['user'].widget.attrs['readonly'] = True
            #self.fields['user'].widget.attrs['disabled'] = True

    class Meta:
        model = UserBook
        exclude = ['book']

#        widgets = {
#                     'user': forms.TextInput(),
#                  } 

admin.site.register(Assignments, AssignmentAdmin)
