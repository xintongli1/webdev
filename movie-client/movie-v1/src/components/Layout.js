import { Outlet } from "react-router-dom";
import React from 'react'

const Layout = () => {
  // This is where the child components will be rendered
  return (
    <main>
      <Outlet />  
    </main>
  )
}

export default Layout
