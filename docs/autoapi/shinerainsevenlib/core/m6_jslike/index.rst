shinerainsevenlib.core.m6_jslike
================================

.. py:module:: shinerainsevenlib.core.m6_jslike


Functions
---------

.. autoapisummary::

   shinerainsevenlib.core.m6_jslike.concat
   shinerainsevenlib.core.m6_jslike.every
   shinerainsevenlib.core.m6_jslike.some
   shinerainsevenlib.core.m6_jslike.filter
   shinerainsevenlib.core.m6_jslike.find
   shinerainsevenlib.core.m6_jslike.findIndex
   shinerainsevenlib.core.m6_jslike.indexOf
   shinerainsevenlib.core.m6_jslike.lastIndexOf
   shinerainsevenlib.core.m6_jslike.map
   shinerainsevenlib.core.m6_jslike.times
   shinerainsevenlib.core.m6_jslike.reduce
   shinerainsevenlib.core.m6_jslike.splice


Module Contents
---------------

.. py:function:: concat(ar1, ar2)

   Like extend, but operates on a copy


.. py:function:: every(lst, fn)

   Return true if the condition holds for all items, will exit early


.. py:function:: some(lst, fn)

   Return true if fn called on any element returns true, exits early


.. py:function:: filter(lst, fn)

   Return a list with items where the condition holds


.. py:function:: find(lst, fn)

   Returns the value in a list where fn returns true, or None


.. py:function:: findIndex(lst, fn)

   Returns the position in a list where fn returns true, or None


.. py:function:: indexOf(lst, valToFind)

   Search for a value and return first position where seen, or -1


.. py:function:: lastIndexOf(lst, valToFind)

   Search for a value and return last position where seen, or -1


.. py:function:: map(lst, fn)

   Return a list with fn called on each item


.. py:function:: times(n, fn)

   Return a list with n items, values from calling fn


.. py:function:: reduce(lst, fn, initialVal=_m2_core_data_structures.DefaultVal)

   Like JS reduce. Callback should have 2 parameters


.. py:function:: splice(s, insertionPoint, lenToDelete=0, newText='')

   Like javascript's splice


