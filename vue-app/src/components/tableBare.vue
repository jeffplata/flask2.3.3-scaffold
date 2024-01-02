<template>
    <table class="table table-hover">
        <thead>
            <tr>
                <th v-for="(fld, index) in fields" v-bind:key="index"
                    @click="onHeaderClick(fld)"
                >
                    <span v-if="(typeof fld==='string')" >
                        [[fld]]
                    </span>
                    <span v-else>[[fld.key]]
                        <i v-if="(['true', true].includes(fld.sortable))" 
                            class="fas"
                            :class="{'fa-sort sort-off': sortBy!=fld.key,
                              'fa-sort-down': sortBy==fld.key && !sortDesc,
                              'fa-sort-up': sortBy==fld.key && sortDesc,
                              }"
                            >
                        </i>
                    </span>
                    <span 
                        v-if="typeof fld==='string' ? sortBy==fld : sortBy==fld.key " 
                        class="badge text-bg-light sort-badge"
                        @click.stop="onClickSortBadge">x</span>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(v1, k1) in items" v-bind:key="k1"
                :class="{'table-active' : v1.selected}"
                @click="onRowClick(v1, k1)">
                <td v-for="(v2, k2) in v1" v-bind:key="k2">
                    <template v-if="fields_simple.includes(k2)">[[v2]]</template></td>
            </tr>
        </tbody>
    </table>
</template>

<script>

export default {
    name: 'table-bare',
    props: ['items', 'fields', 'sortBy', 'sortDesc'],
    setup(props, ctx) {

        const fields_simple = props.fields.map(function(n) {
            if (typeof n==='string') {
                return n
            } else {
                return n.key
            }
        })

        function onClickSortBadge() {
            ctx.emit('changeSortBy', '', '')
        }

        function onHeaderClick(fld) {
            if (typeof fld==='string') {
                ctx.emit('changeSortBy', '', '')
            } else {
                if (fld.key == props.sortBy) {
                    ctx.emit('changeSortBy', fld.key, !props.sortDesc)    
                } else {
                    ctx.emit('changeSortBy', fld.key, false)
                }
            }
        }

        function onRowClick(rowData, idx) {
            ctx.emit('rowClick', rowData, idx)
        }

    return {
        onHeaderClick, onRowClick, fields_simple,
        onClickSortBadge,
    }
    },
}
</script>

<style scoped>
.sort-off {
    color: lightgray
}

.sort-badge {
    cursor: pointer;
    float: right;
}

/* .badge-sm {
    min-width: 1.8em;
    padding: .25em !important;
    margin-left: .1em;
    margin-right: .1em;
    color: white !important;
    cursor: pointer;
} */
</style>