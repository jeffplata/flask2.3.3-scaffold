<template>
    <table class="table table-striped table-hover">
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
                        </i> //TODO: header icons
                    </span>
                </th>
            </tr>
        </thead>
        <tbody>
            <tr v-for="(v1, k1) in items" v-bind:key="k1">
                <td v-for="(v2, k2) in v1" v-bind:key="k2">[[v2]]</td>
            </tr>
        </tbody>
    </table>
</template>

<script>
export default {
    props: ['items', 'fields', 'sortBy', 'sortDesc'],
    setup(props, ctx) {

        function onHeaderClick(fld) {
            console.log(fld.key,)
            if (typeof fld==='string') {
                ctx.emit('changeSortBy', '', '')
            } else {
                if (fld.key == props.sortBy) {
                    ctx.emit('changeSortBy', fld.key, !fld.sortDesc)    
                } else {
                    ctx.emit('changeSortBy', fld.key, false)
                }
            }
        }

    return {
        onHeaderClick
    }
    },
}
</script>

<style scoped>
.sort-off {
    color: lightgray
}
</style>