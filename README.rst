==============
python-irtrans
==============

Indic-to-Roman and Roman-to-Indic transliterator.

Installation
============

Dependencies
~~~~~~~~~~~~

`python-irtrans`_ requires `cython`_, `SciPy`_ and `python-converter-indic`_.

.. _`cython`: http://docs.cython.org/src/quickstart/install.html

.. _`Scipy`: http://www.scipy.org/install.html

.. _`python-converter-indic`: https://github.com/irshadbhat/python-converter-indic

To install the dependencies do something like (Ubuntu):

::

    sudo apt-get install cython
    sudo apt-get install python-scipy

Download
~~~~~~~~

Download **python-irtrans**  from `github`_.

.. _`github`: https://github.com/irshadbhat/python-irtrans

Install
~~~~~~~

::

    cd python-irtrans
    sudo python setup.py install

Examples
~~~~~~~~

1. **Work with Files:**

.. parsed-literal::

    irtrans --h

    --v           show program's version number and exit
    --s source    select language (3 letter ISO-639 code) [hin|tel|guj|eng]
    --t target    select language (3 letter ISO-639 code) [hin|tel|guj|eng]
    --i input     <input-file>
    --f format    select output format [text|ssf|conll|bio|tnt]
    --p ssf-type  specify ssf-type [inter|intra] in case file format (--f) is
                  ssf
    --n           set this flag for nested ssf
    --o output    <output-file>

    Example ::

	irtrans < tests/hindi.txt --s hin --t eng > tests/hindi-rom.txt
	irtrans < tests/roman.txt --s hin --t eng > tests/roman-hin.txt

2. **From Python**

2.1 **Text:**

.. code:: python

    >>> from irtrans import transliterator
    >>> trn = transliterator(source='hin', target='eng')
    >>> 
    >>> text = """आजा सनम मधुर चांदनी में हम-तुम मिले
    ... तो वीराने में भी आ जाएगी बहार
    ... झुमने लगेगा आसमान
    ... कहता है दिल और मचलता है दिल
    ... मोरे साजन ले चल मुझे तारों के पार
    ... लगता नहीं है दिल यहाँ
    ... 
    ... भीगी-भीगी रात में, दिल का दामन थाम ले
    ... खोयी खोयी ज़िन्दगी, हर दम तेरा नाम ले
    ... चाँद की बहकी नज़र, कह रही है प्यार कर
    ... ज़िन्दगी है एक सफ़र, कौन जाने कल किधर
    ... आजा सनम मधुर चांदनी...
    ... 
    ... दिल ये चाहे आज तो, बादल बन उड़ जाऊं मैं
    ... दुल्हन जैसा आसमां, धरती पर ले आऊँ मैं
    ... चाँद का डोला सजे, धूम तारों में मचे
    ... झूम के दुनिया कहे, प्यार में दो दिल मिल
    ... आजा सनम मधुर चांदनी..."""
    >>> 
    >>> print trn.transform(text)
    aaja sanam madhur chaandani men hum-tum mile
    to viraane men bhi a jaaegi bahaar
    jhumne lagega aasmaan
    kahata he dil or machalata he dil
    more saajan le chal mujhe taaron ke paar
    lagta naheen he dil yahan
    
    bheegi-bheegi raat men, dil ka daman tham le
    khoyi khoyi zindagi, har dam tera nam le
    chaand ki baheki nazar, kaha rahi he pyar kar
    zindagi he ek safar, kaun jaane kal kidar
    aaja sanam madhur chaandani...
    
    dil ye chaahe aaj to, badal ban ud jaaun mein
    dulhan jaisa aasmaan, dhrati par le aaun mein
    chaand ka dola saje, dhum taaron men mache
    jhum ke duniya kahe, pyar men do dil mill
    aaja sanam madhur chaandani...
    >>> 

