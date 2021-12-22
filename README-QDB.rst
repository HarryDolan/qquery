Reading the Quicken For Mac Database
====================================

The Fog Lifts
-------------

*It’s my data and I want it back!*

I’ve been managing my personal finances with Quicken since it first came out.
I’ve been mostly happy with it, but had always been irked by the fact that it
kept the data, *my data*, locked up in a proprietary database.  The only way
to get at my data was through Quicken’s limited reporting features or its
limited export capabilities.  My decades of personal data were not available
for me to do the things I wanted to do with them, and I watched with
frustration as the mysterious ``QDATA.QDF`` file grew and grew.

That all changed when I switched from the Windows version to the Mac version
in 
.  Quicken made the switch easy by providing the capability of
importing my data from the Windows version.  But I was delighted to discover
that the Mac version stores my data in a completely open way.  Quicken For Mac
uses the popular and widely used open source
`sqlite <http://sqlite.org/index.html>`_ database.  It was now possible for me
to get at my own data using common tools that are available on any Mac (or
Linux or Windows box).  I just had to poke around a little to figure it out.

Below is what I discovered and how I did it.  Please note that I am a
programmer and have a lot of experience with UNIX command line tools.
The following may be useful to other programmers, but is probably not
immediately useful to others.  Sorry, folks!

Locating the Data
-----------------

Quicken For Mac stores the user data in the directory 
``~/Library/Application Support/Quicken/Documents/Qdata.quicken``

If you go to this directory you will see several files, the largest of which
is named ``data``.  The UNIX file command reveals it to be an sqlite
database: ::

  # cd '~/Library/Application Support/Quicken/Documents/Qdata.quicken'
  # file data
  data: SQLite 3.x database, last written using SQLite version 3019003

That is a beautiful thing to see - data that I can actually work with using
common tools!  But to be safe I always work with a copy of the data, and leave
the contents of this directory alone, *e.g.* ::

   # mkdir ~/playpen
   # cp data ~/playpen/copyofqdata
   # cd ~/playpen

Making Sense of the Database
----------------------------

The primary tool I use here is ``sqlite3`` a command line tool that is already
installed on Macs (and available on Linux and Windows boxes).  There are other
tools available, some graphical, but I am a command line guy.  (By the way,
I’m *not* a database guy - I had to learn it all as I went along).

A relational database is organized as a collection of “tables”.  The tables
are collections of data organized in columns and rows.  Each row of each table
is identified by a unique “primary key” which is how the tables reference data
in other tables.  The first thing to do is to find out what tables are
contained in the database.  This is done with sqlite3’s ‘.tables’ command as
follows. ::

  # sqlite3 copyofqdata ‘.tables’
  ZACCOUNT                       ZLOT                         
  ZACCOUNTTYPE                   ZLOTASSIGNMENT               
  […]

There are actually 27 lines of output in my case, revealing the names of 53
tables.  But what is in those tables?  Here’s a command to list the contents
of the ZACCOUNT table.  A similar command can be used on any of the other
tables.  I will not give the output of the command.  It’s too personal! ::

  # sqlite3 copyofqdata 'select * from ZACCOUNT'|more

There is one line of output for each account I have in Quicken, with the
fields in each line separated by a “|” vertical bar.  Some of the names in
those fields look familiar to me, but what are all those other fields?  The
following command gives the name and types of all those data fields.
There is a lot of output so I will shorten it here. ::

  # sqlite3 copyofqdata ‘.schema ZACCOUNT’
  CREATE TABLE ZACCOUNT ( Z_PK INTEGER PRIMARY KEY, Z_ENT INTEGER,
  Z_OPT INTEGER, ZACTIVE INTEGER, ZCANDIDATENOCASHTRANSACTIONS INTEGER, ZCANDIDATESINGLEMUTUALFUND INTEGER, ZCOSTBASISALGORITHMDEBT INTEGER, ZCOSTBASISALGORITHMMUTUALFUND INTEGER, 
  […]

There are a lot of fields (99 in my case) and they are given all on one line.
So I will use perl to break it to one field per line of output, and more to
print it a page at a time:::

  # sqlite3 copyofqdata ‘.schema ZACCOUNT’|perl -pe 's/,/,\n/g'|more
  CREATE TABLE ZACCOUNT ( Z_PK INTEGER PRIMARY KEY,
  Z_ENT INTEGER,
  Z_OPT INTEGER,
  ZACTIVE INTEGER,
  ZCANDIDATENOCASHTRANSACTIONS INTEGER,
  ZCANDIDATESINGLEMUTUALFUND INTEGER,
  […]

Note that the first field in each table is ``Z_PK``, the primary key.
It is the index that other tables can use to relate to entries in this table.
For example the ``ZTRANSACTION`` table has a field called ``ZACCOUNT`` that is
an integer used to refer to the account in each transaction.  So that one
little field in ``ZTRANSACTION`` makes it possible to avoid storing all the
account information for each transaction.  That’s the power of relational
databases.  But it also makes it a little confusing to figure out what the
data means.

Once I have determined the fields that are interesting to me I can print out
just those.  Instead of ``select *`` I can choose only those fields and see
a lot less output.  For example: ::

  # sqlite3 copyofqdata 'select Z_PK, ZNAME, ZTYPE from ZACCOUNT'

That last field in the output is an index into the ``ZACCOUNTTYPE`` table.
I can use it to look up the account type.  That’s rather laborious, but I can
use the power of SQL to do it for me.  I can “join” the two tables together
as follows: ::

  # sqlite3 copyofqdata 'select ZACCOUNT.Z_PK, ZACCOUNT.ZNAME,
       ZACCOUNTTYPE.ZNAME from ZACCOUNT inner join ZACCOUNTTYPE
       on ZACCOUNT.ZTYPE = ZACCOUNTTYPE.Z_PK'

Now the output is starting to look more familiar, and more readable.

I can repeat the above process for all the tables that appear interesting.
But there are 53 tables, each with dozens of fields.
This is a monstrous database and there may be no hope (or need) to figure it
all out.  After a long and tedious slog I eventually identified the
following tables as the most interesting to me:

=========================   ========================================
ZACCOUNT                    Account data
ZACCOUNTTYPE                Account type names
ZTAG                        Category data
ZUSERPAYEE                  Payee data
ZSECURITY                   Security data (stocks, bonds, etc.)
ZSECURITYQUOTE              Security prices on many different dates
ZPOSITION                   Security “positions”.  Transactions refer to these, which refer to securities.
ZTRANSACTION                Transaction data
ZCASHFLOWTRANSACTIONENTRY   Transaction “splits”, which may be the children of transactions.
=========================   ========================================

This is tedious indeed.  And the data that’s interesting to me will be
different from the data that is interesting to someone else.

Getting the Data I Want
-----------------------

The heart of the data is the transaction list.  Here things can get quite
complicated.  Below is a command to list some interesting fields in all the
transactions: ::

  # sqlite3 copyofqdata 'select zentereddate, zaccount.zname,
    ztransaction.zamount, zuserpayee.zname from ztransaction 
    left join zcashflowtransactionentry 
        on ztransaction.z_pk = zcashflowtransactionentry.zparent 
    left join zaccount on zaccount.z_pk = ztransaction.zaccount 
    left join zuserpayee on zuserpayee.z_pk = ztransaction.zuserpayee'

It’s getting more readable now.   The ouput gives the payee and
account names instead of their primary keys.
This is done by joining to the ``zaccount`` and ``zuserpayee`` tables.
It also joins the transactions with their splits.

But what’s that date field number?  Well, thanks to
`a post on coshxlabs <https://www.coshx.com/blog/2012/12/04/model-of-quicken-mac-essentials-sqlite-database>`_
I was able to figure it out.  The date field is similar to the standard UNIX
way of expressing time as seconds from the January 1, 1970 “epoch”, but
Quicken uses an epoch of January 1, 2001.  That’s a difference of 978307200
seconds.  Here is some python code to do the translation.
Again, my apologies to the non-programmers out there. ::

  import time
  def _formatQuickenDate (qtime):
      # Quicken's epoch is 2001,
      # 31 years after the UNIX epoch of 1970 (978307200 seconds).
      qgmtime = time.gmtime(qtime + 978307200)
      return '{:4}-{:02}-{:02}'.format(qgmtime.tm_year,
                                       qgmtime.tm_mon,
                                       qgmtime.tm_mday)

Talk about tedious!  *Phew!*  It’s clear that this should not be done in
shell scripts, but rather in some high level language such as python.
And I have done just that.  I have written a python package that provides an
easy, intuitive, programatic interface to the database without the programmer
needing to use ``sqlite3`` or complicated SQL queries.  It is
`available on PyPi <https://pypi.python.org/pypi/qquery>`_
and the source code is
`hosted on Github <https://github.com/HarryDolan/qquery>`_.

So what’s next?  I plan to continue to use Quicken since I am still mostly
satisfied with it.  But I am now less vulnerable to capricious decisions
that the developers may make in future versions.  I now have a way of
getting at my data and using it for whatever I choose.
It’s just going to take a bit of programming.
But best of all, I now own my valuable data.
It’s my data and *I got it back!*
