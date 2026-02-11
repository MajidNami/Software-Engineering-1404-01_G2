# Wiki Service  
**Team: NullTerminated**

---

## Overview

The Wiki Service, developed by Team NullTerminated, is a structured
content management module designed to handle geographical and
informational articles within the main system.

This service provides a complete article lifecycle management system,
including categorization, tagging, revision history tracking,
internal article linking, reference management, reporting mechanisms,
and user interaction features such as following articles and
receiving notifications.

It is implemented as a dedicated Django application integrated
within the Core system and operates under the unified project
architecture.

## Architecture

The Wiki Service is implemented as a dedicated Django application
within the Core system and follows the service-oriented architecture
defined for the overall platform.

It is mounted under the `/team6/` URL namespace,
allowing it to operate as a modular component
while remaining fully integrated with the Core routing
and authentication system.

All components are executed inside Docker containers.
The Core container hosts the Django runtime,
while Team6 includes a Gateway (Nginx) container
as part of the standardized deployment structure.

During development, the service operates using Django's
default database configuration within the project environment.
## Project Structure

## How to Run

## URL Structure

## Database

## Features

## Integration with Core

## Notes for Developers
