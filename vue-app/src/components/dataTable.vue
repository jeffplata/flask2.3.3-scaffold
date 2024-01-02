<template>
  <div>

    <CAlert color="info" dismissible>
      <strong>Here</strong> datatables will rise.
    </CAlert>

    
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
                    <CButton
                            @click="editing = adding = true"
                            color="primary"><i class="fa fa-plus"></i>
                            <span class="xxd-none d-md-inline"> Add [[capitalize(title_s)]]</span>
                    </CButton>
                    <span v-if="Object.keys(selected).length===0">
                    <small class="text-muted ms-2" >Click a row to edit or delete.</small>
                    </span>
                    <span v-else>
                        <CButton
                                @click="editing = true"
                                class="ms-1"
                                color="secondary"><i class="fa fa-pencil">
                                </i><span class="d-none d-md-inline"> Edit</span></CButton>
                        <CButton
                                @click="showMsgBoxConfirm"
                                class="ms-1"
                                color="secondary"><i class="fa fa-trash">
                                </i><span class="d-none d-md-inline"> Delete</span></CButton>
                    </span>
                </div>

                <div class="col-sm-5 my-2">
                    <!-- filter box -->
                </div>
            </div>

        <tableBare :items="items"
                   :fields="fields"
                   :sortBy="sortBy"
                   :sortDesc="sortDesc"
                   @changeSortBy="changeSortBy"
                   @rowClick="rowClick"
        ></tableBare>



        <div class="form-row">
          <CInputGroup v-if="totalRows>0">
            <div class="col-xs-4 mr-2">
                <CFormSelect v-model="perPage" :options="perPageOptions" id="perPageOptions" style="width:100px;"></CFormSelect>
            </div>
            <div class="col-xs-8 ms-1">
              <CPagination aria-label="Page navigation example">
                <CPaginationItem aria-label="Previous" href="#"><span aria-hidden="true">&laquo;</span></CPaginationItem>
                <CPaginationItem href="#">1</CPaginationItem>
                <CPaginationItem href="#">2</CPaginationItem>
                <CPaginationItem href="#">3</CPaginationItem>
                <CPaginationItem aria-label="Next" href="#"><span aria-hidden="true">&raquo;</span></CPaginationItem>
              </CPagination>
            </div>
          </CInputGroup>
        </div>

    </div>
    <!-- <div v-else>No data to display.</div> -->

  </div>
</template>



<script>
import DataTable from '@/components/dataTable.js';
import { useCapitalize } from '@/composables/stringUtils';
import { ref } from 'vue';
import tableBare from './tableBare.vue';
import { CAlert, CFormSelect, CInputGroup, CButton,
         CPagination, CPaginationItem,
        } from '@coreui/bootstrap-vue';


export default {
    components: {
    tableBare,
    CAlert, CFormSelect, CInputGroup, CButton,
    CPagination, CPaginationItem,
},
    props: ['apiEndpoint'],
    setup(props) {

        const { flashMessage, flashMessageVariant, 
          adding, editing, title, selected, items, fields,
          currentPage, perPage, perPageOptions, totalRows,
          onRowSelected, onFiltered,
          onSortChanged, onSubmitForm, onPageChange,
          unselectRows,
          sortBy, sortDesc, filter } = DataTable();
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
            }
    }
}

</script>
