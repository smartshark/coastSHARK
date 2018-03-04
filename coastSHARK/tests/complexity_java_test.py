import unittest
import javalang

from coastSHARK.util.complexity_java import ComplexityJava, SourcemeterConversion


BINOP_TEST = """package de.ugoe.cs.coast;

public class BinopTest {

    public void test1() {
        Boolean a = true;
        Boolean b = true;
        Boolean c = true;
        Boolean d = true;
        Boolean e = true;
        Boolean f = true;

        if (a && b && c || d || e && f) {
            // if cc = 1
            // sequence cc = 3
        }
    }

    public void test2() {
        Boolean a = true;
        Boolean b = true;
        Boolean c = true;

        if (a && !(b && c)) {
            // if cc = 1
            // sequence cc = 2
        }
    }

    public void test3() {
        Boolean a = true;
        Boolean b = true;
        Boolean c = true;
        Boolean d = true;
        Boolean e = true;

        if (a && b || c && d || e) {
            // if cc = 1
            // sequence cc = 4
        }
    }

    public void test4() {
        Boolean a = true;
        Boolean b = true;

        if(a == b) {
            // if = 1
            // cc = 1
        } else if (a != b) {
            // cc = 1
        }
    }

    public void test5() {
        Boolean a = true;
        Boolean b = true;

        Boolean c = a && b;
    }

    protected void onActivityResult(int requestCode, int resultCode, Intent data) {
        String resultText = "";
        if (resultCode != RESULT_OK) {
            resultText = "An error occured while contacting OI Safe. Does it allow remote access? (Please check in the settings of OI Safe).";
        } else {
            if (requestCode == ENCRYPT_REQUEST || requestCode == DECRYPT_REQUEST) {
                resultText = data.getStringExtra(CryptoIntents.EXTRA_TEXT);
            } else if (requestCode == SET_PASSWORD_REQUEST) {
                resultText = "Request to set password sent.";
            } else if (requestCode == GET_PASSWORD_REQUEST) {
                String uname = data.getStringExtra(CryptoIntents.EXTRA_USERNAME);
                String pwd = data.getStringExtra(CryptoIntents.EXTRA_PASSWORD);
                resultText = uname + ":" + pwd;
            } else if (requestCode == SPOOF_REQUEST) {
                resultText = data.getStringExtra("masterKey");
            }
        }
        EditText outputText = (EditText) findViewById(R.id.output_entry);
        outputText.setText(resultText, android.widget.TextView.BufferType.EDITABLE);
    }
}
"""

NESTING_TEST = """package de.ugoe.cs.coast;

public class NestingTest {
    public void myMethod() {
        Boolean condition1 = true;
        Boolean condition2 = true;
        try {
            // try does not count towards nesting
            if (condition1) {
                // +1
                for (int i = 0; i < 10; i++) {
                    // +2 (nesting=1)
                    while (condition2) {
                        // +3 (nesting=2)
                    }
                }
            }
        } catch (ExcepType2 e) {
            // +1
            if (condition2) {
                // +2 (nesting=1)
            }
        }
    }
    // sum cc = 9
}
"""

# Sonar does not count default: but we include this in our count
SWITCH_TEST = """package de.ugoe.cs.coast;

public class SwitchTest {

    public String getWords(int number) {   // mccc = +1
        switch (number) {
            case 1:                 // mccc = +1
                return "one";
            case 2:                 // mccc = +1
                return "a couple";
            case 3:                 // mccc = +1
                return "a few";
            default:
                return "lots";
        }
    }

    // mccc = 4
    // cc = 1
}
"""


OVERLOADING_TEST = """package de.ugoe.cs.coast;

public class OverloadingTest {

    public void test(long number) {
    }

    public String test(int number1, int number2) {
    }

    public boolean test(int number1, int number2, boolean test) {
    }
}
"""


PARAM_TEST = """
package de.ugoe.cs.coast;

public class ParamTest {
    public java.lang.String writeAll(java.sql.ResultSet rs, boolean includeColumnNames) throws SQLException, IOException {

        ResultSetMetaData metadata = rs.getMetaData();

        if (includeColumnNames) {
            writeColumnNames(metadata);
        }

        int columnCount = metadata.getColumnCount();

        while (rs.next()) {
            String[] nextLine = new String[columnCount];

            for (int i = 0; i < columnCount; i++) {
                nextLine[i] = getColumnValue(rs, metadata.getColumnType(i + 1), i + 1);
            }

            writeNext(nextLine);
        }
    }
}
"""


CONSTRUCTOR_TEST = """
package de.ugoe.cs.coast;

public class ParamTest {
    public ParamTest(int i) {

    }
}
"""

STATIC_NESTED_TEST = """
package de.ugoe.cs.coast;

public class ParamTest {

    public void test1() {

    }

    static class ParamTest2 {
        public void test2() {

        }
    }
}
"""

ANO_TEST = """
package de.ugoe.cs.coast;

public class AnoTest {

    // nested anonymous class
    BroadcastReceiver mIntentReceiver = new BroadcastReceiver() {
        public void onReceive(Context context, Intent intent) {
            if (intent.getAction().equals(CryptoIntents.ACTION_CRYPTO_LOGGED_OUT)) {
                 if (debug) Log.d(TAG,"caught ACTION_CRYPTO_LOGGED_OUT");
                 startActivity(frontdoor);
            }
        }
    };

    // anonymous class in method
    public void test() {
        // we need to ignore this
        List<String> passDescriptions4Adapter=new ArrayList<String>();

        BroadcastReceiver mIntentReceiver = new BroadcastReceiver() {
            public void onReceive2(Context context, Intent intent) {
                if (intent.getAction().equals(CryptoIntents.ACTION_CRYPTO_LOGGED_OUT)) {
                     if (debug) Log.d(TAG,"caught ACTION_CRYPTO_LOGGED_OUT");
                     startActivity(frontdoor);
                }
            }
        };
    }

    // we want to only count NewDialogInterface and not new AlertDialog, this would otherwise mess with the counting of anonymous classes
    public void test2() {
        dbHelper = new DBHelper(this);
        if (dbHelper.isDatabaseOpen()==false) {
                Dialog dbError = new AlertDialog.Builder(this)
                        .setIcon(android.R.drawable.ic_dialog_alert)
                        .setTitle(R.string.database_error_title)
                        .setPositiveButton(android.R.string.ok, new DialogInterface.OnClickListener() {
                                public void onClick(DialogInterface dialog, int whichButton) {
                                        finish();
                                }
                        })
                        .setMessage(R.string.database_error_msg)
                        .create();
                dbError.show();
                return;
        }
    }

    // anonymous class in method with multiple methods
    public void test3() {
        BroadcastReceiver mIntentReceiver = new BroadcastReceiver() {
            public void naTest1(Context context, Intent intent) {
                if (intent.getAction().equals(CryptoIntents.ACTION_CRYPTO_LOGGED_OUT)) {
                     if (debug) Log.d(TAG,"caught ACTION_CRYPTO_LOGGED_OUT");
                     startActivity(frontdoor);
                }
            }

            public void naTest2() {

            }
        };
    }

    // multi layer inline is not counted (only outermost layer)
    public void test4() {

        BroadcastReceiver mIntentReceiver = new BroadcastReceiver() {
            public void inTest1(Context context, Intent intent) {
                //hallo
                BroadcastReceiver mIntentReceiver = new BroadcastReceiver() {
                    public void sTest1(Context context, Intent intent) {
                        if (intent.getAction().equals(CryptoIntents.ACTION_CRYPTO_LOGGED_OUT)) {
                             if (debug) Log.d(TAG,"caught ACTION_CRYPTO_LOGGED_OUT");
                             startActivity(frontdoor);
                        }
                    }

                    public void sTest2() {

                    }
                };
            }
        };
    }
}
"""

INTERFACE_TEST = """
package de.ugoe.cs.coast;

public interface ITest {
    public int getWordSize();
}
"""


INLINE_INTERFACE_TEST = """
package de.ugoe.cs.coast;

public class InterfaceClass {

    public interface ITest {
        public int getWordSize();
    }
}
"""


CC_TEST = """
package de.ugoe.cs.coast;

public class CCTestClass {
        public long updatePassword(long Id, PassEntry entry) {
                ContentValues args = new ContentValues();
                args.put("description", entry.description);
                args.put("username", entry.username);
                args.put("password", entry.password);
                args.put("website", entry.website);
                args.put("note", entry.note);
                args.put("unique_name", entry.uniqueName);
                DateFormat dateFormatter = DateFormat.getDateTimeInstance(DateFormat.DEFAULT, DateFormat.FULL);
                Date today = new Date();
                String dateOut = dateFormatter.format(today);
                args.put("lastdatetimeedit", dateOut);
                try {
                        db.update(TABLE_PASSWORDS, args, "id=" + Id, null);
                } catch (SQLException e)
                {
                        Log.d(TAG,"updatePassword: SQLite exception: " + e.getLocalizedMessage());
                        return -1;
                }
                return Id;
        }
}
"""

LONG_NAME1 = """org.openintents.safe.CategoryList.onCreateContextMenu(Landroid/view/ContextMenu;Landroid/view/View;Landroid/view/ContextMenu$ContextMenuInfo;)Landroid/app/Dialog;"""
LONG_NAME2 = """org.openintents.safe.SearchFragment.getRowsIds(Ljava/util/List;)[J"""
LONG_NAME3 = """org.openintents.safe.RestoreHandler.characters([CII)V"""
LONG_NAME4 = """org.openintents.safe.Import.doInBackground([Ljava/lang/String;)Ljava/lang/String;"""
LONG_NAME5 = """org.openintents.safe.CryptoContentProvider.insert(Landroid/net/Uri;Landroid/content/ContentValues;)Landroid/net/Uri;"""
LONG_NAME6 = """org.openintents.safe.CryptoContentProvider.query(Landroid/net/Uri;[Ljava/lang/String;Ljava/lang/String;[Ljava/lang/String;Ljava/lang/String;)Landroid/database/Cursor;"""

LONG_NAME7 = """org.openintents.distribution.EulaActivity$1.onClick(Landroid/view/View;)V"""
LONG_NAME8 = """org.openintents.distribution.AboutDialog.<init>(Landroid/content/Context;)V"""
LONG_NAME9 = """estreamj.ciphers.trivium.Trivium$Maker.getName()Ljava/lang/String;"""


NESTED_ANO_TEST = """package de.ugoe.cs.coast;

public class NestedAnoTest {
    
    private class importTask {
        protected void onPostExecute(String result) {
            Dialog about = new AlertDialog.Builder(CategoryList.this)
                                                            .setIcon(R.drawable.passicon)
                                                            .setTitle(R.string.import_complete)
                                                            .setPositiveButton(R.string.yes,
                                                                            new DialogInterface.OnClickListener() {
                                                                                    public void onClick(int whichButton) {
                                                                                            File csvFile = new File(
                                                                                                            importedFilename);
                                                                                            // csvFile.delete();
                                                                                            SecureDelete.delete(csvFile);
                                                                                            importedFilename = "";
                                                                                    }
                                                                            })
                                                            .setNegativeButton(R.string.no,
                                                                            new DialogInterface.OnClickListener() {
                                                                                    public void onClick(DialogInterface dialog,
                                                                                                    int whichButton) {
                                                                                    }
                                                                            }).setMessage(deleteMsg).create();
                                            about.show();

        }
    }
}
"""

# todo:
# - anonymous class in named inner class
# org.openintents.safe.CategoryList$importTask$2.onClick(Landroid/content/DialogInterface;I)V

# import logging, sys

# log = logging.getLogger()
# log.setLevel(logging.DEBUG)
# i = logging.StreamHandler(sys.stdout)
# e = logging.StreamHandler(sys.stderr)

# i.setLevel(logging.DEBUG)
# e.setLevel(logging.ERROR)

# log.addHandler(i)
# log.addHandler(e)


class ComplexityJavaTest(unittest.TestCase):

    def test_nested_ano(self):
        ast = javalang.parse.parse(NESTED_ANO_TEST)
        cj = ComplexityJava(ast)
        m = list(cj.cognitive_complexity())
        self.assertEqual(m[1]['method_name'], 'onClick')
        self.assertEqual(m[1]['class_name'], 'NestedAnoTest$importTask$1')
        self.assertEqual(m[2]['method_name'], 'onClick')
        self.assertEqual(m[2]['class_name'], 'NestedAnoTest$importTask$2')
        self.assertEqual(m[0]['method_name'], 'onPostExecute')
        self.assertEqual(m[0]['class_name'], 'NestedAnoTest$importTask')

    def test_cc_class(self):
        ast = javalang.parse.parse(CC_TEST)
        cj = ComplexityJava(ast)
        m = list(cj.cognitive_complexity())
        self.assertEqual(m[0]['method_name'], 'updatePassword')
        self.assertEqual(m[0]['cyclomatic_complexity'], 1)

    def test_inline_interface(self):
        ast = javalang.parse.parse(INLINE_INTERFACE_TEST)
        cj = ComplexityJava(ast)
        m = list(cj.cognitive_complexity())
        self.assertEqual(m[0]['method_name'], 'getWordSize')
        self.assertEqual(m[0]['class_name'], 'InterfaceClass$ITest')
        self.assertEqual(m[0]['is_interface_method'], True)

    def test_interface(self):
        ast = javalang.parse.parse(INTERFACE_TEST)
        cj = ComplexityJava(ast)
        m = list(cj.cognitive_complexity())
        self.assertEqual(m[0]['method_name'], 'getWordSize')
        self.assertEqual(m[0]['class_name'], 'ITest')
        self.assertEqual(m[0]['is_interface_method'], True)

    def test_anonymous_nested(self):
        ast = javalang.parse.parse(ANO_TEST)
        cj = ComplexityJava(ast)

        # order is not important here, only that we want o have everything with the correct class name
        methods_want = {'onReceive': 'AnoTest$1',
                        'onReceive2': 'AnoTest$2',
                        'onClick': 'AnoTest$3',
                        'naTest1': 'AnoTest$4',
                        'naTest2': 'AnoTest$4',
                        'inTest1': 'AnoTest$5',
                        'sTest1': 'AnoTest$5$1',
                        'sTest2': 'AnoTest$5$1',
                        'test': 'AnoTest',
                        'test2': 'AnoTest',
                        'test3': 'AnoTest',
                        'test4': 'AnoTest'}
        methods_have = set()
        for m in cj.cognitive_complexity():
            self.assertEqual(m['class_name'], methods_want[m['method_name']])
            methods_have.add(m['method_name'])
        self.assertEqual(methods_have, set(methods_want.keys()))

    def test_static_nested(self):
        ast = javalang.parse.parse(STATIC_NESTED_TEST)
        cj = ComplexityJava(ast)

        m = list(cj.cognitive_complexity())
        self.assertEqual(m[1]['method_name'], 'test2')
        self.assertEqual(m[1]['class_name'], 'ParamTest$ParamTest2')

    def test_constructor(self):
        ast = javalang.parse.parse(CONSTRUCTOR_TEST)
        cj = ComplexityJava(ast)

        m = list(cj.cognitive_complexity())
        self.assertEqual(m[0]['parameter_types'], ['int'])
        self.assertEqual(m[0]['return_type'], 'Void')
        self.assertEqual(m[0]['method_name'], '<init>')

    def test_method_params(self):
        ast = javalang.parse.parse(PARAM_TEST)
        cj = ComplexityJava(ast)

        m = list(cj.cognitive_complexity())
        self.assertEqual(m[0]['parameter_types'], ['ResultSet', 'boolean'])
        self.assertEqual(m[0]['return_type'], 'String')

    def test_sourcemeter_conversion(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME1)
        self.assertEqual(tmp[0], ['ContextMenu', 'View', 'ContextMenuInfo'])
        self.assertEqual(tmp[1], 'Dialog')

    def test_sourcemeter_conversion2(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME2)
        self.assertEqual(tmp[0], ['List'])
        self.assertEqual(tmp[1], 'long')

    def test_sourcemeter_conversion3(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME3)
        self.assertEqual(tmp[0], ['char', 'int', 'int'])
        self.assertEqual(tmp[1], 'Void')

    def test_sourcemeter_conversion4(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME4)
        self.assertEqual(tmp[0], ['String'])
        self.assertEqual(tmp[1], 'String')

    def test_sourcemeter_conversion5(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME5)
        self.assertEqual(tmp[0], ['Uri', 'ContentValues'])
        self.assertEqual(tmp[1], 'Uri')

    def test_sourcemeter_conversion6(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME6)
        self.assertEqual(tmp[0], ['Uri', 'String', 'String', 'String', 'String'])
        self.assertEqual(tmp[1], 'Cursor')

    def test_sourcemeter_conversion7(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME7)
        self.assertEqual(tmp[0], ['View'])
        self.assertEqual(tmp[1], 'Void')

    def test_sourcemeter_conversion8(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME8)
        self.assertEqual(tmp[0], ['Context'])
        self.assertEqual(tmp[1], 'Void')

    def test_sourcemeter_conversion9(self):
        sc = SourcemeterConversion()
        tmp = sc.get_sm_params(LONG_NAME9)
        self.assertEqual(tmp[0], [])
        self.assertEqual(tmp[1], 'String')

    def test_overloading(self):
        ast = javalang.parse.parse(OVERLOADING_TEST)
        cj = ComplexityJava(ast)

        l = list(cj.cognitive_complexity())
        self.assertEqual(l[0]['parameter_types'], ['long'])
        self.assertEqual(l[0]['return_type'], 'Void')
        self.assertEqual(l[1]['parameter_types'], ['int', 'int'])
        self.assertEqual(l[1]['return_type'], 'String')
        self.assertEqual(l[2]['parameter_types'], ['int', 'int', 'boolean'])
        self.assertEqual(l[2]['return_type'], 'boolean')

    def test_binary_operation_sequences(self):
        ast = javalang.parse.parse(BINOP_TEST)
        cj = ComplexityJava(ast)

        for m in cj.cognitive_complexity():
            if m['method_name'] == 'test1':
                self.assertEqual(m['cognitive_complexity_sonar'], 4)
                self.assertEqual(m['package_name'], 'de.ugoe.cs.coast')
                self.assertEqual(m['class_name'], 'BinopTest')

            elif m['method_name'] == 'test2':
                self.assertEqual(m['cognitive_complexity_sonar'], 3)

            elif m['method_name'] == 'test3':
                self.assertEqual(m['cognitive_complexity_sonar'], 5)

            elif m['method_name'] == 'test4':
                self.assertEqual(m['cognitive_complexity_sonar'], 3)

            elif m['method_name'] == 'test5':
                self.assertEqual(m['cognitive_complexity_sonar'], 1)

    def test_nesting(self):
        ast = javalang.parse.parse(NESTING_TEST)
        cj = ComplexityJava(ast)

        for m in cj.cognitive_complexity():
            if m['method_name'] == 'myMethod':
                self.assertEqual(m['cognitive_complexity_sonar'], 9)
                self.assertEqual(m['package_name'], 'de.ugoe.cs.coast')
                self.assertEqual(m['class_name'], 'NestingTest')

    def test_switch(self):
        try:
            ast = javalang.parse.parse(SWITCH_TEST)
        except javalang.parser.JavaSyntaxError as e:
            print(e.description)
            print(e.at)

        cj = ComplexityJava(ast)

        for m in cj.cognitive_complexity():
            if m['method_name'] == 'getWords':
                self.assertEqual(m['cognitive_complexity_sonar'], 1)
                self.assertEqual(m['cyclomatic_complexity'], 5)  # we include default: as a branch in switch case
