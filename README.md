# Funder 0.8
Funder is a Django/Wagtail based fundraising application to support online donations 
for Charity and Non Profit's. The flexible 'product' model makes it easy to start a simple 
shop with iDeal checkout options. It's also easy to add your own models to funder.

That being said: funder is a work in progress, this is how it looks now:
![Checkout with iDeal example](docs/images/checkout.png?raw=true)

with some sample products:
![Product page with some examples products](docs/images/products.png?raw=true)



Online demo: [here](https://funder.formatics.nl)

## Quickinstall for developers
`mkvirtualenv funder`
`pip install -r requirements.txt`
`python manage.py migrate`
`python manage.py runserver`

## Status
Funder is a work in progress.

Working features:
- searchable blog with tagging and categories
- searchable products with tagging and categories
- searchable projects with tagging and categories
- working payments via Sisow (iDeal) by using python-sisow
- fully multilingual; translated into 'en' and 'nl'
- extra wagtail admin options for easy access to the custom modules
- easy themeable semantic-ui design

TODO:
- generate nice PDF for billing
- increase supported payment methods
- increase test coverage (only the blog has tests now)
- finish documentation
