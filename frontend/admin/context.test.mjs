import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import test from 'node:test';
import vm from 'node:vm';

function render(candidate) {
  class Element {
    constructor(text='') { this.text=text; this.children=[]; }
    append(...items) { this.children.push(...items); }
    replaceChildren(...items) { this.children=items; }
    setAttribute() {}
    get content() { return this.text+this.children.map(x=>typeof x==='string'?x:x.content).join('\n'); }
  }
  const panel=new Element();
  const context=vm.createContext({$:()=>panel,element:(_tag,text)=>new Element(text)});
  vm.runInContext(readFileSync(new URL('./context.js',import.meta.url),'utf8'),context);
  context.scan={scan_id:'synthetic',runs:[{id:'r',payment:{},review_guidance:{candidates:[candidate]}}]};
  vm.runInContext('renderInvoiceContext(scan)',context);
  return panel.content;
}

test('one bill displays one bank service without unsupported-route warning',()=>{
  const text=render({route:'biller_reference',supported_draft:true,fields:{},warnings:[],
    payment_channels:['Your bank’s CBILL/pagoPA service'],
    payment_note:'Repeated notice; pay only once. Confirmation is simulated.'});
  assert.match(text,/CBILL\/pagoPA service/);
  assert.match(text,/pay only once/);
  assert.match(text,/simulated/);
  assert.doesNotMatch(text,/Payment route needs review/);
});

test('unknown biller route keeps its review warning',()=>{
  const text=render({route:'biller_reference',fields:{},warnings:[]});
  assert.match(text,/Payment route needs review/);
  assert.doesNotMatch(text,/pagoPA/);
});
