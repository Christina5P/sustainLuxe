from django import forms
from .models import UserProfile
from products.models import Product, Size, Condition, Fabric
from decimal import Decimal
from django.utils.safestring import mark_safe
from .models import Account


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = ['full_name', 'email', 'phone_number', 'street_address1', 'postcode', 'town_or_city', 'country']
        exclude = ('user', 'total_revenue')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        placeholders = {
            'full_name': 'Full Name',
            'email': 'Email Address',
            'phone_number': 'Phone Number',
            'street_address1': 'Street Address 1',
            'postcode': 'Postal Code',
            'town_or_city': 'Town or City',
        }
        
        for field in self.fields:
            if field != 'country':
                self.fields[field].widget.attrs['placeholder'] = placeholders.get(field, '')
            self.fields[field].widget.attrs['class'] = 'border-black rounded-0 profile-form-input'
            self.fields[field].label = False


class SellerForm(forms.ModelForm):

    full_name = forms.CharField(
        max_length=255,
        required=True,
        label="Full Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your name'}),
    )

    email = forms.EmailField( 
        max_length=255,
        required=True,
        label="Email",
        widget=forms.TextInput(attrs={'placeholder': 'Enter your email'}),
    )

    phone_number = forms.CharField(
        max_length=20,
        required=True,
        label="Phone Number",
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter your phone number'}
        ),
    )

    street_address = forms.CharField(
        max_length=255,
        required=True,
        label="Street Address",
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter your street address'}
        ),
    )

    postcode = forms.CharField(
        max_length=10,
        required=True,
        label="Postal Code",
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter your postal code'}
        ),
    )

    town_or_city = forms.CharField(
        max_length=100,
        required=True,
        label="Town or City",
        widget=forms.TextInput(
            attrs={'placeholder': 'Enter your town or city'}
        ),
    )

    name = forms.CharField(
        max_length=255,
        required=True,
        label="Product Name",
        widget=forms.TextInput(attrs={'placeholder': 'Enter product name'}),
    )

    SIZE = [
        ('XS', 'XS'),
        ('S', 'S'),
        ('M', 'M'),
        ('L', 'L'),
        ('XL', 'XL'),
      
    ]

    size = forms.ModelChoiceField(
        queryset=Size.objects.all(),
        required=True,
        label="Size",
        widget=forms.Select(attrs={'placeholder': 'Enter size'}),
    )

    price = forms.DecimalField(
        max_digits=10,
        decimal_places=2,
        required=True,
        label="Price",
        widget=forms.NumberInput(attrs={'placeholder': 'Enter price'}),
    )

    CONDITION_CHOICES = [
        ('New with tags', 'New with tags'),
        ('Like new', 'Like new'),
        ('Excellent Condition', 'Excellent Condition'),
        ('Good Condition', 'Good Condition'),
        ('Acceptable', 'Acceptable'),
    ]

    condition = forms.ModelChoiceField(
        queryset=Condition.objects.all(),
        required=True,
        label="Condition",
        widget=forms.Select,
    )

    fabric = forms.ModelChoiceField(
        queryset=Fabric.objects.all(),
        required=True,
        label="Fabric",
        widget=forms.Select,
    )

    weight_in_kg = forms.DecimalField(
        max_digits=5,
        decimal_places=2,
        required=True,
        label="Weight (kg)",
    )

    class Meta:
        model = Product
        fields = [
            'user',
            'full_name',
            'email',
            'phone_number',
            'street_address',
            'postcode',
            'town_or_city',
            'name',
            'price',
            'size',
            'fabric',
            'weight_in_kg',
            'condition',
            'return_option',
        ]


def __init__(self, *args, **kwargs):
    user_profile = kwargs.pop('user_profile', None)
    super().__init__(*args, **kwargs)
    if user_profile:
        self.fields['seller'].initial = user_profile.id
    
    self.fields['return_option'].widget = forms.RadioSelect(choices=[
        (True, 'Pay for a return shipping label'),
        (False, 'Donate unsold items')
    ])
    self.fields['return_option'].label = "Return for unsold product?"


def clean_price(self):
    price = self.cleaned_data.get('price')
    if price <= 0:
        raise forms.ValidationError("Price must be greater than zero.")
    return price


def clean_email(self):
    email = self.cleaned_data.get('email')
    return email


class WithdrawalForm(forms.ModelForm):

    bank_account_number = forms.CharField(
        label='Bank Account Number', max_length=255
    )

    amount = forms.DecimalField(
        label='Withdrawal Amount',
        min_value=Decimal('0.01'),
        max_digits=10,
        decimal_places=2,
        widget=forms.NumberInput(attrs={'step': '0.01'}),
    )

    class Meta:
        model = Account  
        fields = ['amount', 'bank_account_number']

    def __init__(self, *args, **kwargs):
        self.account = kwargs.pop('account', None)
        super().__init__(*args, **kwargs)    

    def clean_amount(self):
        amount = self.cleaned_data['amount']
        if self.account:
            available_balance = self.account.calculate_balance()
            if amount > available_balance:
                raise forms.ValidationError(
                    f"Insufficient funds. Available balance: {available_balance}"
                )
        return amount

    def save(self, commit=True):
        account = super().save(commit=False)
        account.user = self.account.user
        account.bank_account_number = self.cleaned_data['bank_account_number'] 
        print(f"Bank account number: {account.bank_account_number}")
        
        if commit:
            account.save()
        return account
