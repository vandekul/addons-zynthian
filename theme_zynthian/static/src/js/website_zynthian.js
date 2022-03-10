odoo.define('website.website', function (require) {
"use strict";
/* --- Locate the "[!]" string and show the alert banner --- */
console.log("ZYNTHIAN DIRTY TRICKS!");
$(window).on('load',function() {
  /* --- Locate the "[!]" string and show the alert banner --- */
  if ($('h1:contains("[!]")').length>0 || $('table#cart_products:contains("[!]")').length>0) {
    $('.zynthian_alert_message').fadeIn(1000);
  }
  /* --- Locate the "[*]" string and remove "AddToCart button, replacing by "SOLD OUT" warning --- */
  if ($('h1:contains("[*]")').length>0) {
    $('#add_to_cart').hide();
    $('#sold_out_warning').show();
  }
  $('div.oe_product_cart').each(function() {
    if ($(this).find("a[itemprop='name']:contains('[*]')").length>0) {
      $(this).find("a.btn").hide()
    }
  });
});

});

