Complement to Retailer Mexican Localization
==========================================================================

Para completar la información necesaria de este complemento, es necesario:

1. Después de creada la factura, sin validar, llamar el boton
   `Complement Retailer` que se encuentra al inicio de la página de la factura.
2. En este Wizard encontramos varios campos para completar información
    requerida para el mismo, donde:
      - Document Status: Aquí se debe seleccionar el valor para el attributo
        `documentStatus`
      - DeliveryNote: Para este nodo se agregaron los campos
        `referenceIdentification` y `ReferenceDate`, mismos que serán utilizados
        en el CFDI

Para obtener orderIdentification, se necesita colocar en la orden de venta
relacionada en la `Referencia de cliente` el numero de la orden del cliente
seguido de un `|` y la fecha del cliente con el formato YYYY-mmm-dd.


Para buyer, que es la información del comprador, se debe colocar el número
de referencia del partner, ademas de colocar el user_id en el partner,
de donde se obtendrá información del contacto. Además, el buyer deberá tener
asignado un VAT, porque se tomará el valor de ese campo para completar el GLN
(número global de localización).

