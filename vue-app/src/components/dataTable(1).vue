<template>
    <div>
  
      <div class="alert alert-warning alert-dismissible fade show" role="alert">
        <strong>Here</strong> datatables will rise.
        <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
      </div>
  
      <div id="edit_form" v-if="editing" class="edit-section col-md-6 ">
          <h2><div v-if="adding">Add user</div><div v-else>Edit user "form.username"</div></h2>
          <form @submit.prevent="onSubmitForm">
            <slot name="editForm"></slot>
  
            <CButton
                color="primary"
                class="me-1"
                type="submit"
            >Submit</CButton>
  
            <CButton
                @click.prevent="editing = adding = false"
                color="secondary"
                type="cancel"
            >Cancel</CButton>
          </form>
      </div>
  
  
      <div v-if="!editing" class="table-section">
          <h2>[[ capitalize(title) ]]</h2>
              <div v-if="totalRows>0" class="form-row">
  
                  <div class="col-sm-7 my-2">
                      <button
                              @click="editing = adding = true"
                              class="btn btn-primary">
                              <i class="fa fa-plus"></i>
                              <span class="d-none d-md-inline"> Add [[capitalize(title_s)]]</span>
                      </button>
                      <small v-if="Object.keys(selected).length===0" class="text-muted ms-2">
                        Click a row to edit or delete.
                      </small>
                      <span v-else>
                          <CButton
                                  @click="editing = true"
                                  class="ms-1" color="secondary">
                                  <i class="fa fa-pencil"></i>
                                  <span class="d-none d-md-inline"> Edit</span>
                          </CButton>
                          <CButton
                                  @click="showMsgBoxConfirm"
                                  class="ms-1"
                                  color="secondary"><i class="fa fa-trash">
                                  </i><span class="d-none d-md-inline"> Delete</span>
                          </CButton>
                      </span>
                  </div>
  
                  <div class="col-sm-5 my-2">
                      <!-- filter box -->
                  </div>
              </div>
  
          <table-bare :items="items"
                     :fields="fields"
                     :sort-by="sortBy"
                     :sort-desc="sortDesc"
                     @changeSortBy="changeSortBy"
                     @rowClick="rowClick"
          ></table-bare>
  
  
  
          <div v-if="totalRows>0" class="row">
              <div class="col-md-2 mb-1">
                  <select v-model="perPage" class="form-select" id="perPageOptions">
                    <option v-for="(opt, idx) in perPageOptions" v-bind:key="idx" :value="opt.value" >
                      [[opt.label]]
                    </option>
                  </select>
              </div>
              <div class="col-md-8 mb-1">
                <pagination-bare
                  :current-page="currentPage"
                  :total-rows="totalRows"
                  :per-page="perPage"
                  @pageChanged="pageChanged"
                ></pagination-bare>
              </div>
          </div>
  
      </div>
      <!-- <div v-else>No data to display.</div> -->
      <comp-one></comp-one>
      ====
      <compOne></compOne>
  
    </div>
  </template>
  
  
  
  <script>
  import useDataTable from '@/components/dataTable.js';
  import { useCapitalize } from '@/composables/stringUtils';
  import { ref } from 'vue';
  import TableBare from '@/components/tableBare.vue';
  import PaginationBare from '@/components/paginationBare.vue';
  import { CButton, 
          } from '@coreui/bootstrap-vue';
  import CompOne from '@/components/comp1.vue';
  
  export default {
      name: 'data-table',
      components: {
      TableBare, PaginationBare,
      CButton, CompOne
  },
      props: ['apiEndpoint'],
      setup(props) {
  
          const { flashMessage, flashMessageVariant, 
            adding, editing, title, selected, items, fields,
            currentPage, perPage, perPageOptions, totalRows,
            onRowSelected, onFiltered,
            onSortChanged, onSubmitForm, onPageChange,
            unselectRows,
            sortBy, sortDesc, filter } = useDataTable();
          console.log(props.apiEndpoint)
  
          // mutate title
          var title_s
          let title_temp
          title_temp = title.value.split('|')
          title_s = title_temp[0]
          title.value = title_temp.length > 1 ? title_temp[1] : title_temp[0]
  
          editing.value = false
          
          const mybtableRef = ref(null)
  
          function showMsgBoxConfirm() {
            // dummy
          }
  
          function pageChanged(page) {
            currentPage.value = page
            // fetchData('page')
          }
  
          function rowClick(rowData, idx) {
            unselectRows(idx)
            rowData.selected = !rowData.selected
            selected.value = rowData.selected ? [rowData] : []
          }
  
          function changeSortBy(sortByVal, sortDescVal) {
            sortBy.value = sortByVal
            sortDesc.value = sortDescVal
          }
  
          return { 
              flashMessage,
              flashMessageVariant,
              adding,
              editing,
              title, title_s,
              showMsgBoxConfirm,
              selected,
              capitalize:useCapitalize,
              items, fields,
              currentPage, perPage, perPageOptions, totalRows,
              sortBy, sortDesc, filter,
              onRowSelected, onFiltered, onSortChanged,
              onSubmitForm, onPageChange,
              mybtableRef, changeSortBy, rowClick,
              pageChanged,
              }
      }
  }
  
  export {PaginationBare, TableBare, CompOne };
  </script>
  
  <style scoped>
    @import 'bootstrap/dist/css/bootstrap.min.css';
  </style>