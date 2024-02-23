import { StyleSheet, TextInput, View } from "react-native";
import React, { useState } from "react";

import { Ionicons } from "@expo/vector-icons";

const SearchBar = () => {
    const [searchInput, setSearchInput] = useState('');

    const searchHandle = (query : string) =>{
        setSearchInput(query);
       
    }
  return (
    <View style={styles.actionRow}>
      <Ionicons name="search" size={20} color="white" />

      <TextInput
        style={{
          fontFamily: "mon-sb",
          fontSize: 15,
          justifyContent: "center",
          flex: 1,
        }}
        value={searchInput}
        onChangeText={(query) => searchHandle(query)}
        placeholder="Search for pantries or items ..."
        placeholderTextColor="white"
      />

      {/* <TouchableOpacity style = {styles.sortingButton}>
              <FontAwesome name="sort" size={24} color="black"  />
            </TouchableOpacity> */}
    </View>
  );
};

export default SearchBar;

const styles = StyleSheet.create({
  actionRow: {
    flexDirection: "row",
    padding: 15,
    width: 350,
    height: 50,
    borderWidth: 1,
    borderRadius: 30,
    gap: 20,
    marginTop: 20,
    borderColor: "white",
  },
});