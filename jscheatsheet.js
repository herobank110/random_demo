// Comment

/* Multi 
   line comment */

/**
 * Documentation block
 */

// LITERALS

"hello"       // literal string
2             // literal number
[1, 2, 3]     // literal array
{a: 1, b: 2}  // literal object
null          // literal null
undefined     // literal undefined
/hello/       // literal RegExp

// STRINGS

"hello"  // double quotes string
'hello'  // single quotes string
`hello`  // template string
"'"      // double quotes string containing single quote
'"'      // single quotes string containing double quote
""       // empty string

"\""   // escaped double quote
'\''   // escaped single quote
"\n"   // escaped new line
"\r"   // escaped carriage return
"\r\n" // escape carriage return and new line
"\t"   // escaped tab

let myName = "Tony";
"Name = " + myName  // concatenation
`Name = ${myName}`  // template string interpolation

// NUMBERS

2          // number
-2         // number with negative sign
2.5        // number with fraction
1_000_000  // number with digits separator
NaN        // not a number

2     // denary notation
0b10  // binary notation
0o2   // octal notation
0x2   // hexadecimal notation
1e-2  // scientific notation

+  // add
-  // subtract
*  // multiply
/  // divide
%  // modulo

// ARRAYS

[1, 2, 3]         // number array
["a", "b", "c"]   // string array
[1, "b", 3]       // mixed array (avoid)
[[1, 2], [3, 4]]  // nested array

let myArray = [1, 2, 3];
myArray[0]       // get element at index
myArray[0] = 2;  // set element at index

// OBJECTS

{a: 1, b: 2}        // object
{"a": 1, "b c": 2}  // object with quotes around keys to circumvent javascript name rules (eg no spaces)
{1: "a", 2: "b"}    // object with number keys and string values
{}                  // empty object
{a: {b: 2}}         // nested object

let x = "s";
{x: "a"}    // literal key and value => {x: "a"}
{x: x}      // symbolic value => {x: "s"}
{x}         // implicit symbolic value => {x: "s"}
{[x]: "a"}  // symbolic key => {s: "a"}
{[x]: x}    // symbolic key and value => {s: "s"}

let obj = {a: 1, b: 2};
obj.a                // get value with dot operator
obj["a"]             // get value with square bracket operator
obj.a = 3;           // set value with dot operator
obj["a"] = 3;        // set value with square bracket operator
delete object['a'];  // remove key-value pair with square bracket operator
delete object.a;     // remove key-value pair with dot operator

// VARIABLES

var x = 2;         // global/function variable declaration (usually avoid)
let x = 2;         // scoped variable declaration
const x = 2;       // scoped constant declaration
let x;             // declaration without assignment
delete x;          // delete declaration
let x = 2, y = 3;  // multiple declarations

// destructed assignment from array
let arr = [1, 2]
let [a, b] = arr;       // a = 1, b = 2
let [a] = arr;          // pick only first item
let [, b] = arr;        // skip first item
let [a, b, c=2] = arr;  // default value

// destructed assignment from object
let obj = {a: 1, b: 2};
let {a, b} = obj;    // a = 1, b = 2
let {a} = obj;       // pick specific keys
let {a, c=2} = obj;  // default value

// declaration with type comment
/** @type {number} */
let x = 2;





