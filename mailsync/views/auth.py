from mailsync.views.base import BaseView
from mailsync.forms import CreateUserForm
from mailsync.models.auth import user_model
from formencode.validators import Invalid as InvalidForm

class LoginView(BaseView):

    def initialize(self):
        super(LoginView, self).initialize()

    def get(self):

        # Redirect if there are no users in the database
        users = user_model.count_users()
        if users == 0:
            self.redirect("/create_user")
        else:
            message =  self.session.get("message",None)
            errors =  self.session.get("errors",None)
            next = self.get_argument("next", None)
            
            self.delete_session_object("errors")
            self.delete_session_object("message")

            self.render("auth/login.html", message=message, errors=errors, next=next)

    def post(self):
        self.check_xsrf_cookie()
        
        form_data = {
            "username": self.get_argument("username", ""),
            "password": self.get_argument("password", ""),
        }

        user = user_model.check_user(form_data)

        if not user:
            self.session["errors"] = "Invalid login details"
            
            self.redirect("/login")
        else:
            userdata = user.__dict__
            self.session["user"] = {
                "username": userdata["username"],
                "user_id": userdata["_id"]
            }
            
            self.redirect("/")

class LogoutView(BaseView):

    def initialize(self):
        super(LogoutView, self).initialize()

    def get(self):
        self.delete_session_object("user")    
        self.redirect("/login")

class CreateUserView(BaseView):

    def initialize(self):
        super(CreateUserView, self).initialize()

    def get(self):
        errors = self.session.get("errors", None)
        form_data = self.session.get("form_data", None)

        users = user_model.count_users()

        if users == 0:
            self.render("auth/create_user.html", errors=errors, form_data=form_data)
        else:
            self.redirect("/login")
        
    def post(self):
        self.check_xsrf_cookie()

        form_data = {
            "username": self.get_argument("username", ""),
            "password": self.get_argument("password",""),
        }
        
        try:
            valid_data = CreateUserForm.to_python(form_data)
            user_model.create_user(valid_data)
            self.session["message"] = "Account successfuly created. You can now log in"

            self.delete_session_object("errors")
            self.delete_session_object("form_data")

            self.redirect("/login")

        except InvalidForm, e:
            self.session["errors"] = e.unpack_errors()
            self.session["form_data"] = form_data

            self.redirect("/create_user")